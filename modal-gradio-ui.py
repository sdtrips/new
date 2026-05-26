"""
Gradio UI on Modal CPU — serverless, pay-per-use.
Now with model selection support.

The UI runs on Modal's cheap CPU tier (~$0.001/hr). When the user clicks
"Generate", it calls the Modal GPU worker via HTTP. The GPU only fires
during actual generation.

Deploy: modal deploy modal-gradio-ui.py
Requires: modal-gpu-worker.py already deployed (for the API URL)
"""

import modal
import os

# Container image — lightweight, no torch, no GPU
image = modal.Image.debian_slim(python_version="3.12").uv_pip_install(
    "gradio==5.*",
    "requests==2.32.*",
    "pillow==11.*",
)

# --- MODIFY THESE ---
GPU_API_URL = "https://your-org--gpu-generator-image.modal.run"
GPU_VIDEO_API_URL = "https://your-org--gpu-generator-video.modal.run"
# --- END CONFIG ---

app = modal.App("gradio-ui")

# Model display options (sync with modal-gpu-worker.py)
IMAGE_MODEL_OPTIONS = {
    "flux-schnell": "⚡ Flux.1 Schnell",
    "flux-dev": "🎨 Flux.1 Dev",
    "sd35-turbo": "🖼️ SD3.5 Turbo",
    "sdxl": "🎭 SDXL",
}
VIDEO_MODEL_OPTIONS = {
    "ltx-video": "⚡ LTX-Video",
    "mochi": "🎬 Mochi 1",
    "wan-14b": "🎥 Wan 2.1 14B",
}
DEFAULT_IMAGE = "flux-schnell"
DEFAULT_VIDEO = "ltx-video"


@app.cls(
    image=image,
    cpu=1.0,       # CPU only — no GPU
    memory=512,    # 512MB is enough for Gradio
    secrets=[modal.Secret.from_name("api-auth")],
    container_idle_timeout=60,  # Shut down after 60s idle → $0
)
class GradioUI:
    @modal.asgi_app()
    def web(self):
        import gradio as gr
        import requests
        import base64
        from io import BytesIO
        from PIL import Image

        API_TOKEN = os.environ.get("API_TOKEN", "")

        def gen_image(prompt, model_key):
            try:
                r = requests.post(
                    GPU_API_URL,
                    json={"prompt": prompt, "model_name": model_key},
                    headers={"x-api-token": API_TOKEN},
                    timeout=120,
                )
                if r.status_code != 200:
                    return None
                data = r.json()
                if "image" not in data:
                    return None
                return Image.open(BytesIO(base64.b64decode(data["image"])))
            except:
                return None

        def gen_video(prompt, model_key):
            try:
                r = requests.post(
                    GPU_VIDEO_API_URL,
                    json={"prompt": prompt, "model_name": model_key},
                    headers={"x-api-token": API_TOKEN},
                    timeout=300,
                )
                if r.status_code != 200:
                    return None
                video = base64.b64decode(r.json()["video"])
                path = "/tmp/video.mp4"
                with open(path, "wb") as f:
                    f.write(video)
                return path
            except:
                return None

        with gr.Blocks(title="🎨 المولّد") as demo:
            gr.Markdown("## 🎨 مولّد الصور والفيديو")

            with gr.Tab("🖼️ صورة"):
                t = gr.Textbox(label="الوصف", lines=3)
                m1 = gr.Dropdown(
                    choices=list(IMAGE_MODEL_OPTIONS.values()),
                    value=IMAGE_MODEL_OPTIONS[DEFAULT_IMAGE],
                    label="النموذج",
                )
                b = gr.Button("توليد", variant="primary")
                out = gr.Image(label="النتيجة")

                def on_img(p, m):
                    k = DEFAULT_IMAGE
                    for key, val in IMAGE_MODEL_OPTIONS.items():
                        if val == m:
                            k = key
                            break
                    return gen_image(p, k)

                b.click(on_img, [t, m1], out)

            with gr.Tab("🎬 فيديو"):
                t2 = gr.Textbox(label="الوصف", lines=3)
                m2 = gr.Dropdown(
                    choices=list(VIDEO_MODEL_OPTIONS.values()),
                    value=VIDEO_MODEL_OPTIONS[DEFAULT_VIDEO],
                    label="النموذج",
                )
                b2 = gr.Button("توليد", variant="primary")
                out2 = gr.Video(label="النتيجة")

                def on_vid(p, m):
                    k = DEFAULT_VIDEO
                    for key, val in VIDEO_MODEL_OPTIONS.items():
                        if val == m:
                            k = key
                            break
                    return gen_video(p, k)

                b2.click(on_vid, [t2, m2], out2)

        return demo
