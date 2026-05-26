# Video Generation Models Catalog

Verified May 2026 from HuggingFace download counts and Modal examples.

## Model Cards

### LTX-Video (Lightricks) ⚡ — FASTEST
- **Model ID:** `Lightricks/LTX-Video`
- **Downloads:** ~435K
- **Parameters:** ~2B
- **GPU Min:** L40S, **GPU Rec:** H100
- **VRAM:** ~24GB
- **Resolution:** 480p (768×480 default)
- **Speed:** 2-15s for 5-20s clip (warm container)
- **$1 yields:** ~50-300 videos (H100)
- **Modal Example:** ✅ `06_gpu_and_ml/text-to-video/ltx.py`, `06_gpu_and_ml/image-to-video/image_to_video.py`
- **Use case:** Fast prototyping, high volume, good quality
- **Note:** Also supports image-to-video with the same model

### Mochi 1 (Genmo) 🎥 — HIGH QUALITY
- **Model ID:** `genmo/mochi-1-preview`
- **Downloads:** ~8K
- **Parameters:** ~10B
- **GPU Min:** H100 only (needs ~40GB VRAM)
- **VRAM:** ~40GB
- **Resolution:** 480p-720p
- **Speed:** 3-5 min for ~5s clip (64 steps)
- **$1 yields:** ~3 videos (H100)
- **Cost/video:** ~$0.33 (Modal example confirms)
- **Modal Example:** ✅ `06_gpu_and_ml/text-to-video/mochi.py`
- **Use case:** High quality, cinematic, when quality > speed

### LTX-2 (Lightricks) 🎵 — VIDEO + AUDIO
- **Model ID:** `Lightricks/LTX-2` (also `Lightricks/LTX-2.3` with ~2.2M downloads)
- **Parameters:** 19B
- **GPU Min:** H200 required (needs ~80GB+ VRAM)
- **VRAM:** ~80GB+
- **Resolution:** 1024×1536 (2-stage: half-res → upscale 2x)
- **Speed:** 5-15 min for ~5s clip with synchronized audio
- **$1 yields:** ~0.6-1.3 videos (H200)
- **Modal Example:** ✅ `06_gpu_and_ml/text-to-video/ltx2_two_stage.py`
- **Use case:** Production-grade, video + audio, highest quality
- **Note:** Requires Gemma 3 license acceptance + HuggingFace token (Modal Secret `huggingface-secret`)

### Wan2.1 / Wan2.2 (Wan-AI) 🌟 — VERSATILE
Multiple model sizes for different budgets:

| Model | Params | GPU Min | $1 yields | Speed | Downloads |
|-------|--------|---------|-----------|-------|-----------|
| Wan2.1 T2V-1.3B | 1.3B | L40S+ | ~60-120 | 10-30s | 135K |
| Wan2.2 I2V-5B | 5B | L40S+ | ~30-60 | 20-40s | 124K |
| Wan2.1 T2V-14B | 14B | A100/H100 | ~30-50 | 30-60s | 57K |
| Wan2.1 I2V-14B-480P | 14B | A100/H100 | ~30-50 | 30-60s | 93K |
| Wan2.1 I2V-14B-720P | 14B | A100/H100 | ~20-40 | 45-90s | 57K |
| Wan2.2 T2V-14B | 14B | A100/H100 | ~30-50 | 30-60s | 102K |

- **Model IDs:** `Wan-AI/Wan2.1-*` / `Wan-AI/Wan2.2-*`
- **Use case:** Best flexibility from lightweight to high quality
- **Note:** No official Modal example but straightforward to deploy via diffusers

### CogVideoX (Zhipu AI / Tsinghua) 🎬
- **Model IDs:** `zai-org/CogVideoX-2b`, `zai-org/CogVideoX-5b`, `zai-org/CogVideoX-5b-I2V`
- **Downloads:** 27-33K each
- **Parameters:** 2B or 5B
- **GPU Min:** L40S (2B), A100-80GB (5B)
- **Resolution:** 480p-720p
- **Speed:** 30-60s (2B), 1-2 min (5B)
- **$1 yields:** ~30-60 (2B), ~15-30 (5B)
- **Use case:** Well-supported in diffusers, Chinese AI lab

### HunyuanVideo (Tencent) 🎥
- **Model ID:** `tencent/HunyuanVideo-1.5` (~1.9K downloads), `tencent/HunyuanVideo` (~885 downloads)
- **Parameters:** ~13B
- **GPU Min:** A100-80GB (needs ~60GB VRAM)
- **Resolution:** 720p
- **Speed:** 2-5 min
- **$1 yields:** ~4-15 videos
- **Use case:** Strong cinematic quality

### Stable Video Diffusion (Stability AI) 🖼️→🎬
- **Model IDs:** `stabilityai/stable-video-diffusion-img2vid-xt` (264K downloads)
- **Parameters:** ~2B
- **GPU Min:** A100/H100
- **Speed:** 10-30s
- **$1 yields:** ~60-120 videos
- **Use case:** Image-to-video only, well-established

### Open-Sora (HPC-AI Tech) 📖
- **Model IDs:** `hpcai-tech/OpenSora-STDiT-v3`, `hpcai-tech/Open-Sora-v2`
- **Parameters:** 1.1B-3B
- **GPU Min:** L40S/A100
- **Speed:** 30-60s
- **$1 yields:** ~30-60 videos
- **Use case:** Research-focused, good quality

## Summary: GPU Tier → Best Model

| GPU | Best Video Model | Why |
|-----|------------------|-----|
| **T4** (16GB) | Wan2.1 T2V-1.3B | Only light model that fits |
| **L40S** (48GB) | LTX-Video, CogVideoX-2B | Best speed/quality balance |
| **A100-80GB** (80GB) | HunyuanVideo, CogVideoX-5B | Mid-range high quality |
| **H100** (80GB) | Mochi 1, Wan2.1-14B, LTX-Video | All models. Best all-rounder |
| **H200** (141GB) | LTX-2 | Only GPU that runs LTX-2 |
