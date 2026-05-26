"""
Gradio UI for Modal GPU Worker — with model selection dropdown
Runs on VPS (or any always-on server)

Setup:
  pip install gradio requests pillow
  export API_URL="https://your-org--gpu-generator-image.modal.run"
  export API_VIDEO_URL="https://your-org--gpu-generator-video.modal.run"
  export API_TOKEN="your-secret-key"
  export ADMIN_USER="admin"
  export ADMIN_PASS="your-password"
  python vps-gradio-ui.py

Coolify / Docker setup:
  Set these environment variables in the Coolify dashboard:
    API_URL, API_VIDEO_URL, API_TOKEN, ADMIN_USER, ADMIN_PASS

Keep alive with systemd:
  [Unit]
  Description=Gradio UI
  After=network.target

  [Service]
  Environment="API_URL=..."
  Environment="API_TOKEN=..."
  Environment="ADMIN_USER=admin"
  Environment="ADMIN_PASS=mypass"
  ExecStart=/usr/bin/python3 /path/to/vps-gradio-ui.py
  Restart=always

  [Install]
  WantedBy=multi-user.target
"""

import gradio as gr
import requests
import base64
from io import BytesIO
from PIL import Image
import os
import json

# --- Configuration from environment ---
API_URL = os.getenv("API_URL", "https://your-org--gpu-generator-image.modal.run")
API_VIDEO_URL = os.getenv("API_VIDEO_URL", "https://your-org--gpu-generator-video.modal.run")
API_TOKEN = os.getenv("API_TOKEN", "my-secret-key")
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASS = os.getenv("ADMIN_PASS", "mypassword123")


# ============================================================
# MODEL CATALOG — Sync this with modal-gpu-worker.py
# ============================================================
# These are the display names for the dropdown.
# The API sends the short key (e.g. "flux-schnell") to the GPU worker.
# ============================================================

IMAGE_MODELS = {
    "flux-schnell": "⚡ Flux.1 Schnell — سريع جداً (~$0.003)",
    "flux-dev": "🎨 Flux.1 Dev — جودة عالية (~$0.015)",
    "sd35-turbo": "🖼️ SD3.5 Large Turbo (~$0.003)",
    "sdxl": "🎭 SDXL — كلاسيكي (~$0.005)",
}

VIDEO_MODELS = {
    "ltx-video": "⚡ LTX-Video — سريع جداً (~$0.02)",
    "mochi": "🎬 Mochi 1 — جودة عالية (~$0.33)",
    "wan-14b": "🎥 Wan 2.1 14B — ممتاز (~$0.05)",
}

# Default selection
DEFAULT_IMAGE_MODEL = "flux-schnell"
DEFAULT_VIDEO_MODEL = "ltx-video"

# Order for dropdown display
IMAGE_MODEL_KEYS = ["flux-schnell", "flux-dev", "sd35-turbo", "sdxl"]
VIDEO_MODEL_KEYS = ["ltx-video", "mochi", "wan-14b"]


# --- API callers ---
def gen_image(prompt: str, model_key: str):
    """Call Modal GPU worker to generate image."""
    try:
        r = requests.post(
            API_URL,
            json={"prompt": prompt, "model_name": model_key},
            headers={"x-api-token": API_TOKEN},
            timeout=120,
        )
        if r.status_code == 401:
            return None, "❌ خطأ في التوكن — تأكد من API_TOKEN"
        if r.status_code != 200:
            return None, f"❌ خطأ {r.status_code}: {r.text}"

        data = r.json()
        if "image" in data:
            img = Image.open(BytesIO(base64.b64decode(data["image"])))
            model_name = data.get("model_name", model_key)
            return img, f"✅ تم — النموذج: {model_name}"
        return None, f"❌ {data.get('error', 'خطأ غير معروف')}"
    except requests.exceptions.Timeout:
        return None, "❌ انتهت المهلة — النموذج يستغرق وقتًا أطول من المتوقع"
    except Exception as e:
        return None, f"❌ خطأ في الاتصال: {str(e)}"


def gen_video(prompt: str, model_key: str):
    """Call Modal GPU worker to generate video."""
    try:
        r = requests.post(
            API_VIDEO_URL,
            json={"prompt": prompt, "model_name": model_key},
            headers={"x-api-token": API_TOKEN},
            timeout=300,
        )
        if r.status_code == 401:
            return None, "❌ خطأ في التوكن — تأكد من API_TOKEN"
        if r.status_code != 200:
            return None, f"❌ خطأ {r.status_code}: {r.text}"

        data = r.json()
        if "video" in data:
            video_bytes = base64.b64decode(data["video"])
            path = "/tmp/generated_video.mp4"
            with open(path, "wb") as f:
                f.write(video_bytes)
            model_name = data.get("model_name", model_key)
            return path, f"✅ تم — النموذج: {model_name}"
        return None, f"❌ {data.get('error', 'خطأ غير معروف')}"
    except requests.exceptions.Timeout:
        return None, "❌ انتهت المهلة — النموذج يستغرق وقتًا أطول من المتوقع"
    except Exception as e:
        return None, f"❌ خطأ في الاتصال: {str(e)}"


# --- Check API health on startup ---
try:
    health_url = API_URL.rsplit("/", 1)[0] + "/health"
    r = requests.get(health_url, timeout=5)
    info = r.json()
    print(f"✅ Modal API connected:")
    print(f"   Image model: {info.get('image_model', '?')}")
    print(f"   Video model: {info.get('video_model', '?')}")
    print(f"   Available: {info.get('available_image_models', [])}")
except Exception as e:
    print(f"⚠️  Could not reach Modal API: {e}")
    print(f"   Make sure API_URL is correct and modal deploy has run.")


# --- Build Gradio UI ---
with gr.Blocks(
    title="🎨 المولّد السحري",
    theme=gr.themes.Soft(),
    auth=(ADMIN_USER, ADMIN_PASS),
) as demo:
    gr.Markdown("""
    # 🎨 المولّد السحري

    اكتب وصف الصورة أو الفيديو. الأول مرة تحتاج ~15-30 ثانية (تحميل النموذج)،
    بعدها التوليد يكون سريعًا.

    > 🔒 واجهة محمية — الرجاء تسجيل الدخول
    > 💰 الدفع فقط وقت طلب التوليد، التصفح مجاني
    > 🧠 **يمكنك اختيار النموذج** من القائمة المنسدلة أسفل!
    """)

    with gr.Tab("🖼️ صورة"):
        with gr.Row():
            with gr.Column(scale=2):
                prompt = gr.Textbox(
                    label="📝 الوصف",
                    lines=4,
                    placeholder="اكتب وصف الصورة بالعربية أو الإنجليزية...\nمثال: قط يرتدي بدلة رسمية، إضاءة سينمائية",
                )

                model_choice = gr.Dropdown(
                    choices=[IMAGE_MODELS[k] for k in IMAGE_MODEL_KEYS],
                    value=IMAGE_MODELS[DEFAULT_IMAGE_MODEL],
                    label="🧠 اختر النموذج",
                    info="تغيير النموذج قد يأخذ 10-30 ثانية لتحميله أول مرة",
                    interactive=True,
                )

                btn = gr.Button("✨ توليد الصورة", variant="primary", size="lg")
                status = gr.Textbox(label="الحالة", interactive=False)
            with gr.Column(scale=3):
                output = gr.Image(label="النتيجة", height=500)

        def on_image_click(prompt_text, model_display):
            # Map display text back to model key
            model_key = DEFAULT_IMAGE_MODEL
            for k, v in IMAGE_MODELS.items():
                if v == model_display:
                    model_key = k
                    break
            return gen_image(prompt_text, model_key)

        btn.click(on_image_click, [prompt, model_choice], [output, status])

    with gr.Tab("🎬 فيديو"):
        with gr.Row():
            with gr.Column(scale=2):
                prompt2 = gr.Textbox(
                    label="📝 الوصف",
                    lines=4,
                    placeholder="اكتب وصف الفيديو...\nمثال: حصان يجري على شاطئ البحر عند الغروب",
                )

                model_choice2 = gr.Dropdown(
                    choices=[VIDEO_MODELS[k] for k in VIDEO_MODEL_KEYS],
                    value=VIDEO_MODELS[DEFAULT_VIDEO_MODEL],
                    label="🧠 اختر النموذج",
                    info="تغيير النموذج قد يأخذ 10-30 ثانية لتحميله أول مرة",
                    interactive=True,
                )

                btn2 = gr.Button("✨ توليد الفيديو", variant="primary", size="lg")
                status2 = gr.Textbox(label="الحالة", interactive=False)
            with gr.Column(scale=3):
                output2 = gr.Video(label="النتيجة", height=500)

        def on_video_click(prompt_text, model_display):
            # Map display text back to model key
            model_key = DEFAULT_VIDEO_MODEL
            for k, v in VIDEO_MODELS.items():
                if v == model_display:
                    model_key = k
                    break
            return gen_video(prompt_text, model_key)

        btn2.click(on_video_click, [prompt2, model_choice2], [output2, status2])

    gr.Markdown("---")
    with gr.Accordion("ℹ️ معلومات", open=False):
        gr.Markdown(f"""
        - **خادم الصور:** `{API_URL}`
        - **خادم الفيديو:** `{API_VIDEO_URL}`
        - ⏱️ أول طلب: ~10-30 ثانية (تحميل النموذج)
        - ⚡ الطلبات التالية لنفس النموذج: ~1-15 ثانية
        - 🔄 تغيير النموذج: ~10-30 ثانية
        - 🧠 اختر النموذج المناسب لمهمتك من القائمة المنسدلة
        """)


if __name__ == "__main__":
    import socket
    hostname = socket.gethostname()
    print(f"🚀 الواجهة جاهزة على http://0.0.0.0:7860")
    print(f"👤 المستخدم: {ADMIN_USER}")
    print(f"🔑 كلمة السر: {ADMIN_PASS}")

    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        auth=(ADMIN_USER, ADMIN_PASS),
    )
