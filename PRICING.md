# Modal GPU Pricing Reference

Source: Modal.com official pricing + Modal example code (Mochi example confirms ~$5/hr for H100). Verified May 2026.

## GPU Options & Pricing

| GPU | VRAM | Memory BW | Architecture | $/hour | Notes |
|-----|------|-----------|-------------|--------|-------|
| T4 | 16GB | 320 GB/s | Turing | ~$1.47 | Entry-level. SDXL, small models |
| L4 | 24GB | 300 GB/s | Ada Lovelace | ~$1.50 | Good for Flux schnell |
| A10G | 24GB | 600 GB/s | Ampere | ~$2.00 | Cloud-optimized. Good balance |
| L40S | 48GB | 864 GB/s | Ada Lovelace | ~$2.17 | Great for 48GB models. Recommended mid-range |
| A100-40GB | 40GB | 1555 GB/s | Ampere | ~$3.47 | Older gen, still capable |
| A100-80GB | 80GB | 2039 GB/s | Ampere | ~$4.81 | Double VRAM. HunyuanVideo territory |
| H100 | 80GB | 3352 GB/s | Hopper | ~$5.27 | Recommended. Fastest support. All models run |
| H200 | 141GB | 4800 GB/s | Hopper | ~$6.62 | For 19B+ models (LTX-2) |
| H200 (DGX) | 141GB x8 | N/A | Hopper | ~$8.00+ | Multi-GPU setup |
| B200 | ~180GB | 8000 GB/s | Blackwell | ~$8.00 | Newest gen, cutting-edge |
| RTX-PRO-6000 | 48GB | 960 GB/s | Ada Lovelace | ~$4.00 | Workstation GPU |

## GPU Memory Requirements by Model

| Model | Min VRAM | Rec VRAM | GPU Recommendation |
|-------|----------|----------|-------------------|
| SDXL | 8GB | 16GB | T4, L4 |
| Flux.1-schnell (fp16) | 16GB | 24GB | L4, A10G, L40S |
| Flux.1-dev (fp16) | 24GB | 48GB | L40S, A100 |
| SD3.5 Medium | 16GB | 24GB | A10G, L40S |
| SD3.5 Large | 24GB | 48GB | L40S, A100 |
| LTX-Video | 24GB | 48GB | L40S, H100 (opt) |
| Wan2.1 T2V-1.3B | 8GB | 16GB | T4, L4 |
| Wan2.1 T2V-14B | 48GB | 80GB | A100-80GB, H100 |
| CogVideoX-2B | 16GB | 24GB | L40S |
| CogVideoX-5B | 40GB | 80GB | A100-80GB, H100 |
| Mochi 1 | 40GB | 80GB | H100 only |
| HunyuanVideo | 60GB | 80GB | A100-80GB, H100 |
| LTX-2 (19B) | 80GB | 141GB | H200 required |

## Cost Calculation Formula

```
cost = (gpu_hourly_rate / 3600) × inference_seconds
```

**Examples (H100 at $5.27/hr):**
- Image (2 sec): $5.27/3600 × 2 = **$0.003**
- Video (15 sec): $5.27/3600 × 15 = **$0.022**
- Video (4 min): $5.27/3600 × 240 = **$0.35**

**Cold start cost:**
- Container boot (~3s): $0.004
- Model load from Volume (~10s): $0.015
- Total cold start: **~$0.02**
- First-ever (download from HF, ~5min): **~$0.44**

## Key Config Options

```python
@app.cls(
    gpu="H100",
    container_idle_timeout=300,  # Keep warm 5 min after last request ($0)
    timeout=600,                # Max run time before force-kill
    scaledown_window=15*60,     # DEPRECATED — use container_idle_timeout
)
```

Setting `container_idle_timeout=300` means:
- After last request, container stays warm for 5 minutes
- No GPU cost during idle (container is suspended, pay only for storage ~$0)
- Next request within 5 min = instant (no cold start)
