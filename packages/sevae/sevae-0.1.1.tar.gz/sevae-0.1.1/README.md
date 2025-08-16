# SEVAE: Structural Equation–VAE

Interpretable, disentangled latents for tabular data via a theory-driven architecture.  
SEVAE mirrors structural-equation modeling (SEM): each **construct** has its own encoder/decoder block, plus an optional **nuisance (“method”)** latent and **global cross-talk** context.

## Features
- **Per-construct latents** (`K` constructs × `d_per_construct`)
- **Global cross-talk** (`context_dim`) concatenated to each construct encoder
- **Nuisance latent(s)** over the full input (`n_nuisance_blocks × d_nuisance`)
- **Adversarial leakage penalty** 
- **KL annealing** via a single knob (`cfg.kl_weight`) you can change during training
- **Flexible column indexing**:
  - contiguous blocks via `items_per_construct` (default),
  - arbitrary **index lists** with `model.bind_column_groups([...])`,
  - **name-based** with `cfg.feature_name_groups` + `model.bind_feature_names(names)`.

## Install

```bash
# 1) Install a matching Torch wheel for your platform (CPU or CUDA)
#    (example for CUDA 12.1 — change as needed)
pip install torch --index-url https://download.pytorch.org/whl/cu121
# or simply: pip install torch  (CPU wheels)

# 2) Install SEVAE
pip install sevae
# or: pip install 'sevae[torch]'  (declares a torch extra)
```

## Quickstart

```bash
import torch
from sevae import SEVAE, SEVAEConfig

K, J = 6, 8

cfg = SEVAEConfig(
    n_constructs=K,
    items_per_construct=J,     # contiguous groups: [F1 items][F2 items]...[FK items]
    d_per_construct=1,
    d_nuisance=1,
    n_nuisance_blocks=1,
    context_dim=1,             # small cross-talk like "global_context"
    hidden=128,
    dropout=0.05,
    # structure losses (can start at 0 and tune later)
    tc_weight=6.4,
    ortho_weight=1.0,
    leakage_weight=0.5,
    # KL weight is a knob you can anneal while training
    kl_weight=0.0
)
model = SEVAE(cfg)

x = torch.randn(64, K * J)
out = model(x)           # forward
losses = model.loss(x, out)
(losses["loss_total"]).backward()
```

## Flexible column indexing
A) Arbitrary index groups
```bash
# Suppose your 48 columns are interleaved. Provide groups explicitly:
column_groups = [
    [0,  7, 14, 21, 28, 35, 42, 47],  # construct 0 item indices
    [1,  8, 15, 22, 29, 36, 43, 46],  # construct 1
    # ...
]
model.bind_column_groups(column_groups)
```
B) Name-based groups
```bash
# If you have pandas columns, bind by names once:
cfg = SEVAEConfig(
    n_constructs=K,
    items_per_construct=J,
    feature_name_groups=[
        [f"F1_Item{j}" for j in range(1, J+1)],
        [f"F2_Item{j}" for j in range(1, J+1)],
        # ...
    ],
    context_dim=1,
)
model = SEVAE(cfg)
model.bind_feature_names(df.columns.tolist())
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
