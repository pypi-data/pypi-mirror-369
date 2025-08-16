# src/sevae/models/sevae.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Sequence, Tuple, Dict, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F


@dataclass
class SEVAEConfig:
    n_constructs: int
    items_per_construct: Sequence[int] | int
    d_per_construct: int = 1                     # latent dims per construct
    d_nuisance: int = 1                          # dims per nuisance block
    n_nuisance_blocks: int = 1                   # how many nuisance "sets"
    hidden: int = 128
    dropout: float = 0.0
    context_dim: int = 0                         # 0 disables global context encoder
    tc_weight: float = 0.0
    ortho_weight: float = 0.0
    leakage_weight: float = 0.5                  # 0 disables adversarial leakage loss


class SEVAE(nn.Module):
    """
    Structural Equation–VAE with:
      - per-construct encoders/decoders
      - optional global context encoder
      - one or more nuisance encoders (concatenated)
      - adversarial leakage decoders on nuisance latents
    """
    def __init__(self, cfg: SEVAEConfig):
        super().__init__()
        self.cfg = cfg

        # Normalize items_per_construct to a list[int]
        if isinstance(cfg.items_per_construct, int):
            self.items_per_construct: List[int] = [cfg.items_per_construct] * cfg.n_constructs
        else:
            assert len(cfg.items_per_construct) == cfg.n_constructs, \
                "items_per_construct list must match n_constructs"
            self.items_per_construct = list(cfg.items_per_construct)

        self.input_dim = sum(self.items_per_construct)
        K = cfg.n_constructs

        # ---------- Global context encoder (optional) ----------
        if cfg.context_dim > 0:
            self.global_context = nn.Sequential(
                nn.Linear(self.input_dim, cfg.hidden),
                nn.ReLU(),
                nn.Dropout(cfg.dropout),
                nn.Linear(cfg.hidden, K * cfg.context_dim),
            )
        else:
            self.global_context = None

        # ---------- Per-construct encoders ----------
        self.factor_encoders = nn.ModuleList()
        for j_k in self.items_per_construct:
            in_dim = j_k + (cfg.context_dim if cfg.context_dim > 0 else 0)
            self.factor_encoders.append(
                nn.Sequential(
                    nn.Linear(in_dim, cfg.hidden),
                    nn.ReLU(),
                    nn.Dropout(cfg.dropout),
                    nn.Linear(cfg.hidden, 2 * cfg.d_per_construct),  # mu || logvar
                )
            )

        # ---------- Nuisance encoders (one or more blocks) ----------
        self.nuisance_encoders = nn.ModuleList()
        for _ in range(cfg.n_nuisance_blocks):
            self.nuisance_encoders.append(
                nn.Sequential(
                    nn.Linear(self.input_dim, cfg.hidden),
                    nn.ReLU(),
                    nn.Dropout(cfg.dropout),
                    nn.Linear(cfg.hidden, 2 * cfg.d_nuisance),        # mu || logvar
                )
            )

        # total nuisance dimension passed to decoders
        self.d_nuisance_total = cfg.n_nuisance_blocks * cfg.d_nuisance

        # ---------- Per-construct decoders ----------
        self.decoders = nn.ModuleList()
        for j_k in self.items_per_construct:
            self.decoders.append(
                nn.Sequential(
                    nn.Linear(cfg.d_per_construct + self.d_nuisance_total, cfg.hidden),
                    nn.ReLU(),
                    nn.Dropout(cfg.dropout),
                    nn.Linear(cfg.hidden, j_k),
                )
            )

        # ---------- Adversarial decoders (leakage suppression) ----------
        self.adversarial_decoders = nn.ModuleList()
        for j_k in self.items_per_construct:
            self.adversarial_decoders.append(
                nn.Sequential(
                    nn.Linear(self.d_nuisance_total, max(16, cfg.hidden // 2)),
                    nn.ReLU(),
                    nn.Linear(max(16, cfg.hidden // 2), j_k),
                )
            )

    # ----------- helpers -----------
    @staticmethod
    def _reparam(mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        std = torch.exp(0.5 * logvar)
        eps = torch.randn_like(std)
        return mu + eps * std

    def _split_groups(self, x: torch.Tensor) -> List[torch.Tensor]:
        """Split flat x into construct groups as contiguous chunks."""
        chunks = []
        start = 0
        for j_k in self.items_per_construct:
            chunks.append(x[:, start:start + j_k])
            start += j_k
        return chunks

    # ----------- encode/decode -----------
    def encode(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        B = x.size(0)
        K = self.cfg.n_constructs
        ctx_chunks: Optional[List[torch.Tensor]] = None

        if self.global_context is not None:
            ctx = self.global_context(x)                          # [B, K * context_dim]
            ctx_chunks = list(torch.chunk(ctx, K, dim=1))         # K * [B, context_dim]

        x_groups = self._split_groups(x)

        zc_mu = []
        zc_logvar = []
        for k, enc in enumerate(self.factor_encoders):
            x_in = x_groups[k] if ctx_chunks is None else torch.cat([x_groups[k], ctx_chunks[k]], dim=1)
            h = enc(x_in)
            mu, logvar = torch.split(h, self.cfg.d_per_construct, dim=1)
            zc_mu.append(mu)
            zc_logvar.append(logvar)

        zc_mu = torch.cat(zc_mu, dim=1)                 # [B, K * d_per_construct]
        zc_logvar = torch.cat(zc_logvar, dim=1)

        # nuisance blocks
        zn_mu_blocks, zn_logvar_blocks = [], []
        for enc in self.nuisance_encoders:
            h = enc(x)
            mu, logvar = torch.split(h, self.cfg.d_nuisance, dim=1)
            zn_mu_blocks.append(mu)
            zn_logvar_blocks.append(logvar)

        zn_mu = torch.cat(zn_mu_blocks, dim=1)          # [B, n_blocks * d_nuisance]
        zn_logvar = torch.cat(zn_logvar_blocks, dim=1)

        return {"zc_mu": zc_mu, "zc_logvar": zc_logvar, "zn_mu": zn_mu, "zn_logvar": zn_logvar}

    def decode(self, zc: torch.Tensor, zn: torch.Tensor) -> torch.Tensor:
        """Decode each construct group from its local latent + concatenated nuisance."""
        B = zc.size(0)
        K = self.cfg.n_constructs
        d = self.cfg.d_per_construct
        x_hats = []
        for k, dec in enumerate(self.decoders):
            z_k = zc[:, k * d:(k + 1) * d]
            x_hat_k = dec(torch.cat([z_k, zn], dim=1))
            x_hats.append(x_hat_k)
        return torch.cat(x_hats, dim=1)                 # [B, input_dim]

    # ----------- forward -----------
    def forward(self, x: torch.Tensor) -> Dict[str, torch.Tensor]:
        enc = self.encode(x)
        zc = self._reparam(enc["zc_mu"], enc["zc_logvar"])
        zn = self._reparam(enc["zn_mu"], enc["zn_logvar"])
        x_hat = self.decode(zc, zn)
        return {"x_hat": x_hat, **enc, "zc": zc, "zn": zn}

    # ----------- losses -----------
    @staticmethod
    def kl_normal(mu: torch.Tensor, logvar: torch.Tensor) -> torch.Tensor:
        """KL(q||p) to N(0,I); returns mean over batch."""
        return -0.5 * (1 + logvar - mu.pow(2) - logvar.exp()).sum(dim=1).mean()

    @staticmethod
    def _tc_loss(z: torch.Tensor) -> torch.Tensor:
        # Simple covariance off-diagonal penalty (proxy for TC)
        zc = z - z.mean(0, keepdim=True)
        cov = (zc.T @ zc) / (zc.size(0) - 1)
        off = cov - torch.diag(torch.diag(cov))
        return (off ** 2).sum()

    @staticmethod
    def _orthogonality_loss(z_blocks: List[torch.Tensor]) -> torch.Tensor:
        # Encourage decorrelation across construct subspaces
        if len(z_blocks) <= 1:
            return torch.zeros((), device=z_blocks[0].device)
        Z = torch.cat(z_blocks, dim=1)
        Zc = Z - Z.mean(0, keepdim=True)
        gram = (Zc.T @ Zc) / (Zc.size(0))
        off = gram - torch.diag(torch.diag(gram))
        return (off ** 2).sum()

    def leakage_loss(self, x: torch.Tensor, zn: torch.Tensor) -> torch.Tensor:
        """Adversarial leakage: penalize reconstructing x_k from nuisance alone."""
        chunks = self._split_groups(x)
        losses = []
        for k, adv in enumerate(self.adversarial_decoders):
            xk = chunks[k]
            xk_hat_adv = adv(zn.detach())
            losses.append(F.mse_loss(xk_hat_adv, xk, reduction="mean"))
        return torch.stack(losses).mean()

    def loss(self, x: torch.Tensor, out: Dict[str, torch.Tensor]) -> Dict[str, torch.Tensor]:
        x_hat, zc, zn = out["x_hat"], out["zc"], out["zn"]
        zc_mu, zc_logvar, zn_mu, zn_logvar = out["zc_mu"], out["zc_logvar"], out["zn_mu"], out["zn_logvar"]

        recon = F.mse_loss(x_hat, x, reduction="mean")
        kl_c = self.kl_normal(zc_mu, zc_logvar)
        kl_n = self.kl_normal(zn_mu, zn_logvar)

        # Build blocks for orthogonality across constructs
        K, d = self.cfg.n_constructs, self.cfg.d_per_construct
        z_blocks = [zc[:, k * d:(k + 1) * d] for k in range(K)]

        tc = self._tc_loss(torch.cat([zc, zn], dim=1)) if self.cfg.tc_weight > 0 else torch.zeros_like(recon)
        ortho = self._orthogonality_loss(z_blocks) if self.cfg.ortho_weight > 0 else torch.zeros_like(recon)
        leak = self.leakage_loss(x, zn) if self.cfg.leakage_weight > 0 else torch.zeros_like(recon)

        total = recon + kl_c + kl_n + self.cfg.tc_weight * tc + self.cfg.ortho_weight * ortho + self.cfg.leakage_weight * leak
        return {
            "loss_total": total,
            "loss_recon": recon,
            "loss_kl_construct": kl_c,
            "loss_kl_nuisance": kl_n,
            "loss_tc": tc,
            "loss_ortho": ortho,
            "loss_leakage": leak,
        }