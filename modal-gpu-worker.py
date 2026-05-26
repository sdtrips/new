"""
Modal GPU Worker for Image & Video Generation
Supports switching models via API request (model_name parameter).

Deploy: modal deploy modal-gpu-worker.py
Requires: modal secret create api-auth API_TOKEN=your-secret-key

Architecture:
  [Gradio UI / curl] → POST /image or /video → Modal GPU Worker (H100)
                                                     ↓
                                              Returns base64 encoded media

Usage with model selection:
  curl -X POST https://your-org--gpu-generator-image.modal.run \
    -H "x-api-token: YOUR_TOKEN" \
    -d '{"prompt": "cat in space", "model_name": "flux-schnell"}'
"""

import modal

app = modal.App("gpu-generator")

# --- Container Image ---
image = (
    modal.Image.debian_slim(python_version="3.12")
    .uv_pip_install(
        "diffusers==0.33.1",
        "torch==2.7.0",
        "accelerate==1.6.0",
        "transformers==4.51.3",
        "huggingface-hub==0.36.0",
        "imageio==2.37.0",
        "imageio-ffmpeg==0.6.1",
        "sentencepiece==0.2.0",
    )
    .env({"HF_HUB_CACHE": "/models", "HF_XET_HIGH_PERFORMANCE": "1"})
)

# --- Persistent model storage ---
models_volume = modal.Volume.from_name("models-store", create_if_missing=True)

# ============================================================
# MODEL CATALOG — Add/remove models here
# ============================================================
# To add a new model, just add an entry below. The UI dropdown
# will auto-populate from these dicts.

IMAGE_MODELS = {
    "flux-schnell": {
        "id": "black-forest-labs/FLUX.1-schnell",
        "name": "Flux.1 Schnell",
        "steps": 4,
        "desc": "⚡ سريع جداً (4 خطوات) — جودة ممتازة",
        "min_gpu": "L40S",
        "cost": "~$0.003/صورة",
    },
    "flux-dev": {
        "id": "black-forest-labs/FLUX.1-dev",
        "name": "Flux.1 Dev",
        "steps": 28,
        "desc": "🎨 جودة عالية (28 خطوة) — يحتاج وقت أطول",
        "min_gpu": "A100",
        "cost": "~$0.015/صورة",
    },
    "sd35-turbo": {
        "id": "stabilityai/stable-diffusion-3.5-large-turbo",
        "name": "SD3.5 Large Turbo",
        "steps": 4,
        "desc": "🖼️ دقة 1024px — جودة ممتازة",
        "min_gpu": "H100",
        "cost": "~$0.003/صورة",
    },
    "sdxl": {
        "id": "stabilityai/stable-diffusion-xl-base-1.0",
        "name": "SDXL",
        "steps": 30,
        "desc": "🎭 كلاسيكي — متوافق مع أغلب الأدوات",
        "min_gpu": "T4",
        "cost": "~$0.005/صورة",
    },
}

VIDEO_MODELS = {
    "ltx-video": {
        "id": "Lightricks/LTX-Video",
        "name": "LTX-Video",
        "frames": 49,
        "steps": 20,
        "desc": "⚡ سريع جداً — ~2 ثانية فيديو",
        "min_gpu": "L40S",
        "cost": "~$0.02/فيديو",
    },
    "mochi": {
        "id": "genmo/mochi-1-preview",
        "name": "Mochi 1",
        "frames": 25,
        "steps": 50,
        "desc": "🎬 جودة عالية — ~5 ثواني فيديو",
        "min_gpu": "H100",
        "cost": "~$0.33/فيديو",
    },
    "wan-14b": {
        "id": "Wan-AI/Wan2.1-T2V-14B",
        "name": "Wan 2.1 (14B)",
        "frames": 81,
        "steps": 30,
        "desc": "🎥 جودة ممتازة — يدعم 720p",
        "min_gpu": "A100",
        "cost": "~$0.05/فيديو",
    },
}

# Default models
DEFAULT_IMAGE = "flux-schnell"
DEFAULT_VIDEO = "ltx-video"

# ============================================================


@app.cls(
    gpu="H100",
    image=image,
    volumes={"/models": models_volume},
    timeout=600,
    container_idle_timeout=300,
    secrets=[modal.Secret.from_name("api-auth")],
)
class GPUWorker:
    def __init__(self):
        self.image_pipe = None
        self.video_pipe = None
        self._current_image_model = None
        self._current_video_model = None

    @modal.enter()
    def load_defaults(self):
        """Load default models when container starts."""
        import os
        print(f"📦 Loading default image model: {DEFAULT_IMAGE}")
        self._load_image_model(DEFAULT_IMAGE)
        print(f"📦 Loading default video model: {DEFAULT_VIDEO}")
        self._load_video_model(DEFAULT_VIDEO)

    def _load_image_model(self, model_name: str):
        """Load an image model by key from IMAGE_MODELS dict."""
        import torch

        if model_name == self._current_image_model and self.image_pipe is not None:
            return  # Already loaded

        cfg = IMAGE_MODELS.get(model_name)
        if not cfg:
            raise ValueError(f"❌ Unknown image model: {model_name}")

        print(f"🔄 Loading image model: {cfg['id']} ...")
        from diffusers import FluxPipeline, StableDiffusion3Pipeline, DiffusionPipeline

        model_id = cfg["id"]

        # Free up memory if switching models
        if self.image_pipe is not None:
            del self.image_pipe
            torch.cuda.empty_cache()

        # Flux models use FluxPipeline, others use DiffusionPipeline
        if "flux" in model_id.lower():
            self.image_pipe = FluxPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.bfloat16,
            ).to("cuda")
        elif "stable-diffusion" in model_id.lower() or "sdxl" in model_id.lower():
            self.image_pipe = DiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.bfloat16,
            ).to("cuda")
        else:
            self.image_pipe = DiffusionPipeline.from_pretrained(
                model_id,
                torch_dtype=torch.bfloat16,
            ).to("cuda")

        self._current_image_model = model_name
        print(f"✅ Image model loaded: {cfg['name']}")

    def _load_video_model(self, model_name: str):
        """Load a video model by key from VIDEO_MODELS dict."""
        import torch

        if model_name == self._current_video_model and self.video_pipe is not None:
            return  # Already loaded

        cfg = VIDEO_MODELS.get(model_name)
        if not cfg:
            raise ValueError(f"❌ Unknown video model: {model_name}")

        print(f"🔄 Loading video model: {cfg['id']} ...")
        from diffusers import DiffusionPipeline

        model_id = cfg["id"]

        # Free up memory if switching models
        if self.video_pipe is not None:
            del self.video_pipe
            torch.cuda.empty_cache()

        self.video_pipe = DiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.bfloat16,
        ).to("cuda")

        self._current_video_model = model_name
        print(f"✅ Video model loaded: {cfg['name']}")

    def _auth(self, headers):
        """Validate API token."""
        import os
        token = (
            headers.get("x-api-token") or
            headers.get("authorization", "").replace("Bearer ", "")
        )
        return token == os.environ.get("API_TOKEN", "")

    @modal.web_endpoint(method="POST", docs=True)
    def image(self, data: dict, headers: dict = {}) -> dict:
        """Generate image from text prompt.

        Request:
          {"prompt": "a cat in space"}
          {"prompt": "a cat", "model_name": "flux-dev"}  (optional model switch)
          {"prompt": "a cat", "width": 1024, "height": 768}

        Response:
          {"image": "<base64 PNG>", "model": "flux-schnell"}
        """
        if not self._auth(headers):
            return {"error": "Unauthorized"}, 401

        prompt = data.get("prompt", "")
        width = data.get("width", 1024)
        height = data.get("height", 1024)
        model_name = data.get("model_name", self._current_image_model or DEFAULT_IMAGE)

        try:
            self._load_image_model(model_name)
        except ValueError as e:
            return {"error": str(e)}, 400

        cfg = IMAGE_MODELS[model_name]

        img = self.image_pipe(
            prompt,
            num_inference_steps=cfg["steps"],
            width=width,
            height=height,
            guidance_scale=0.0,
        ).images[0]

        import io, base64
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return {
            "image": base64.b64encode(buf.getvalue()).decode(),
            "model": model_name,
            "model_name": cfg["name"],
        }

    @modal.web_endpoint(method="POST", docs=True)
    def video(self, data: dict, headers: dict = {}) -> dict:
        """Generate video from text prompt.

        Request:
          {"prompt": "a horse galloping"}
          {"prompt": "a horse", "model_name": "mochi"}  (optional model switch)

        Response:
          {"video": "<base64 MP4>", "model": "ltx-video"}
        """
        if not self._auth(headers):
            return {"error": "Unauthorized"}, 401

        prompt = data.get("prompt", "")
        model_name = data.get("model_name", self._current_video_model or DEFAULT_VIDEO)

        try:
            self._load_video_model(model_name)
        except ValueError as e:
            return {"error": str(e)}, 400

        from diffusers.utils import export_to_video
        import base64

        cfg = VIDEO_MODELS[model_name]

        frames = self.video_pipe(
            prompt,
            num_frames=cfg["frames"],
            num_inference_steps=cfg["steps"],
        ).frames[0]

        export_to_video(frames, "/tmp/output.mp4", fps=24)

        with open("/tmp/output.mp4", "rb") as f:
            return {
                "video": base64.b64encode(f.read()).decode(),
                "model": model_name,
                "model_name": cfg["name"],
            }

    @modal.web_endpoint(method="GET")
    def health(self) -> dict:
        """Health check — no auth required."""
        return {
            "status": "ok",
            "image_model": self._current_image_model,
            "video_model": self._current_video_model,
            "available_image_models": list(IMAGE_MODELS.keys()),
            "available_video_models": list(VIDEO_MODELS.keys()),
        }

    @modal.web_endpoint(method="GET")
    def models(self) -> dict:
        """Return available models catalog — no auth required."""
        return {
            "image_models": {
                k: {
                    "name": v["name"],
                    "desc": v["desc"],
                    "min_gpu": v["min_gpu"],
                    "cost": v["cost"],
                    "steps": v["steps"],
                }
                for k, v in IMAGE_MODELS.items()
            },
            "video_models": {
                k: {
                    "name": v["name"],
                    "desc": v["desc"],
                    "min_gpu": v["min_gpu"],
                    "cost": v["cost"],
                    "steps": v["steps"],
                    "frames": v["frames"],
                }
                for k, v in VIDEO_MODELS.items()
            },
        }
