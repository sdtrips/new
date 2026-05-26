"""
Modal GPU Worker for Image & Video Generation

Deploy: modal deploy modal-gpu-worker.py
Requires: modal secret create api-auth API_TOKEN=your-secret-key

Architecture:
  [Gradio UI / curl] → POST /image or /video → Modal GPU Worker (H100)
                                                     ↓
                                              Returns base64 encoded media
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

# --- Image Model ---
# Change MODEL_ID to switch models:
#   "black-forest-labs/FLUX.1-schnell"  (fast, 4 steps)
#   "black-forest-labs/FLUX.1-dev"       (quality, 50 steps)
#   "stabilityai/stable-diffusion-3.5-large-turbo"
#   "stabilityai/stable-diffusion-xl-base-1.0"
IMAGE_MODEL_ID = "black-forest-labs/FLUX.1-schnell"
IMAGE_STEPS = 4  # 4 for schnell, 28-50 for dev

# --- Video Model ---
# Change VIDEO_MODEL_ID to switch:
#   "Lightricks/LTX-Video"           (fast, 2B params)
#   "genmo/mochi-1-preview"          (quality, 10B, H100 only)
VIDEO_MODEL_ID = "Lightricks/LTX-Video"
VIDEO_FRAMES = 49  # ~2 seconds at 24fps
VIDEO_STEPS = 20


@app.cls(
    gpu="H100",
    image=image,
    volumes={"/models": models_volume},
    timeout=600,
    container_idle_timeout=300,
    secrets=[modal.Secret.from_name("api-auth")],
)
class GPUWorker:
    @modal.enter()
    def load(self):
        """Load models once when container starts."""
        import os
        import torch
        from diffusers import FluxPipeline, DiffusionPipeline
        
        self.image_pipe = FluxPipeline.from_pretrained(
            IMAGE_MODEL_ID,
            torch_dtype=torch.bfloat16,
        ).to("cuda")
        
        self.video_pipe = DiffusionPipeline.from_pretrained(
            VIDEO_MODEL_ID,
            torch_dtype=torch.bfloat16,
        ).to("cuda")
    
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
        
        Request: {"prompt": "a cat in space"}
        Response: {"image": "<base64 PNG>"}
        """
        if not self._auth(headers):
            return {"error": "Unauthorized"}, 401
        
        prompt = data.get("prompt", "")
        width = data.get("width", 1024)
        height = data.get("height", 1024)
        
        img = self.image_pipe(
            prompt,
            num_inference_steps=IMAGE_STEPS,
            width=width,
            height=height,
            guidance_scale=0.0,
        ).images[0]
        
        import io, base64
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return {"image": base64.b64encode(buf.getvalue()).decode()}
    
    @modal.web_endpoint(method="POST", docs=True)
    def video(self, data: dict, headers: dict = {}) -> dict:
        """Generate video from text prompt.
        
        Request: {"prompt": "a horse galloping"}
        Response: {"video": "<base64 MP4>"}
        """
        if not self._auth(headers):
            return {"error": "Unauthorized"}, 401
        
        from diffusers.utils import export_to_video
        import base64
        
        prompt = data.get("prompt", "")
        
        frames = self.video_pipe(
            prompt,
            num_frames=VIDEO_FRAMES,
            num_inference_steps=VIDEO_STEPS,
        ).frames[0]
        
        export_to_video(frames, "/tmp/output.mp4", fps=24)
        
        with open("/tmp/output.mp4", "rb") as f:
            return {"video": base64.b64encode(f.read()).decode()}
    
    @modal.web_endpoint(method="GET")
    def health(self) -> dict:
        """Health check — no auth required."""
        return {"status": "ok", "image_model": IMAGE_MODEL_ID, "video_model": VIDEO_MODEL_ID}
