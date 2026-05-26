# Image Generation Models Catalog

Verified May 2026 from HuggingFace download counts and Modal examples.

## Model Cards

### Flux.1 (Black Forest Labs) ⚡🔥 — BEST OVERALL
Two variants:
- **schnell:** 4 inference steps, fast, good quality
- **dev:** 50 steps, higher quality, slower

| Variant | Model ID | Downloads | GPU Min | Rec GPU | Speed | $1 yields |
|---------|----------|-----------|---------|---------|-------|-----------|
| **schnell** | `black-forest-labs/FLUX.1-schnell` | ~595K | L40S/A10G | H100 | 1-2s | ~900-1800 |
| **dev** | `black-forest-labs/FLUX.1-dev` | ~708K | A100/H100 | H100 | 5-15s | ~120-360 |
| **Fill-dev** | `black-forest-labs/FLUX.1-Fill-dev` | ~275K | A100/H100 | H100 | 10-20s | — |
| **Fill-schnell** | — | — | L40S+ | H100 | 2-4s | — |

- **VRAM:** 16GB+ (schnell), 24GB+ (dev)
- **Resolution:** 1024×1024 (native), supports arbitrary aspect ratios
- **Cost/image (H100):** ~$0.003 (schnell), ~$0.015 (dev)
- **Modal Example:** ✅ `06_gpu_and_ml/stable_diffusion/flux.py` (uses torch.compile)
- **Use case:** #1 recommendation. Best quality-to-speed ratio in open source.
- **Note:** Gated model — requires license acceptance on HuggingFace. Use `huggingface-secret` Modal Secret.

### Stable Diffusion 3.5 (Stability AI) 🎨
Three variants:

| Variant | Model ID | Downloads | GPU Min | Speed | $1 yields |
|---------|----------|-----------|---------|-------|-----------|
| **Medium** | `stabilityai/stable-diffusion-3.5-medium` | ~347K | L40S/A10G+ | 2-5s | ~360-900 |
| **Large** | `stabilityai/stable-diffusion-3.5-large` | ~34K | A100/H100 | 5-15s | ~120-360 |
| **Large Turbo** | `stabilityai/stable-diffusion-3.5-large-turbo` | ~7K | H100 | 1-2s | ~900-1800 |

- **Resolution:** 1024×1024
- **Modal Example (Large Turbo):** ✅ `06_gpu_and_ml/stable_diffusion/text_to_image.py`
- **Use case:** Solid alternative to Flux. Large Turbo matches Flux schnell in speed.

### SDXL (Stability AI) 💪 — BUDGET KING
- **Model ID:** `stabilityai/stable-diffusion-xl-base-1.0`
- **GPU Min:** T4 (works!)
- **Rec GPU:** L4, A10G
- **Speed:** 5-10s (T4), 2-4s (L40S+)
- **Resolution:** 1024×1024
- **$1 yields:** ~180-360 (T4), ~360-720 (L40S)
- **Use case:** Best when GPU budget is tight. Works on T4 ($1.47/hr).

### SD3.5 ControlNet variants
- Available for pose, depth, canny, etc.
- Same GPU requirements as base model
- Adds 1-2s overhead per image

## Summary: GPU Tier → Best Image Model

| GPU | Best Image Model | Why |
|-----|------------------|-----|
| **T4** (16GB) | **SDXL** | Only major model that fits and runs fast enough |
| **L4** (24GB) | **Flux.1-schnell** | Fits in 24GB, much better quality than SDXL |
| **A10G** (24GB) | **Flux.1-schnell** | Same as L4 but faster |
| **L40S** (48GB) | **Flux.1-schnell**, **SD3.5 Medium** | Both fit comfortably |
| **A100/H100** (80GB) | **All models** | Run everything |
