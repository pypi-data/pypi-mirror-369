# SEVAE: Structural Equation–VAE

Interpretable, disentangled latents for tabular data via theory-driven architecture.

## Install

```bash
# install your preferred Torch first (CPU or CUDA)
pip install torch --index-url https://download.pytorch.org/whl/cu121   # or plain pip for CPU
pip install sevae
```

## Quickstart

```bash
import torch
from sevae import SEVAE, SEVAEConfig

cfg = SEVAEConfig(
  n_constructs=6, items_per_construct=8,
  d_per_construct=1, d_nuisance=2, n_nuisance_blocks=2,
  context_dim=16, hidden=128, leakage_weight=0.5, tc_weight=6.4, ortho_weight=1.0
)
model = SEVAE(cfg)

x = torch.randn(64, 6*8)
out = model(x)
losses = model.loss(x, out)
losses["loss_total"].backward()
```

## Citation

Zhang, R., Zhao, C., Zhao, X., Nie, L., & Lam, W. F. (2025). Structural Equation-VAE: Disentangled Latent Representations for Tabular Data. arXiv preprint arXiv:2508.06347.
```bash
@article{zhang2025structural,
  title={Structural Equation-VAE: Disentangled Latent Representations for Tabular Data},
  author={Zhang, Ruiyu and Zhao, Ce and Zhao, Xin and Nie, Lin and Lam, Wai-Fung},
  journal={arXiv preprint arXiv:2508.06347},
  year={2025}
}
```
