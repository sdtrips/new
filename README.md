# Serverless Media Generation Deployment 🎨🎬

نشر موديلات توليد الصور والفيديو مفتوحة المصدر على **Modal.com** باستخدام GPU سيرفرلس (تدفع فقط عند الاستخدام). مع إمكانية **اختيار النموذج** من الواجهة مباشرة!

## 📋 الملفات

| الملف | الوصف |
|-------|-------|
| `modal-gpu-worker.py` | 🖥️ **GPU Worker** — يدعم تبديل الموديلات عبر API |
| `vps-gradio-ui.py` | 🌐 **واجهة Gradio (VPS)** — مع dropdown لاختيار الموديل |
| `modal-gradio-ui.py` | ☁️ **واجهة Gradio (Modal CPU)** — مع اختيار الموديل |
| `Dockerfile` | 🐳 للنشر على **Coolify** أو أي Docker host |
| `requirements-ui.txt` | 📦 متطلبات الواجهة (خفيفة) |
| `COOLIFY.md` | 🚀 دليل نشر Coolify كامل |
| `PRICING.md` | 💰 أسعار GPUs المختلفة على Modal |
| `IMAGE-MODELS.md` | 🖼️ كتالوج موديلات الصور |
| `VIDEO-MODELS.md` | 🎬 كتالوج موديلات الفيديو |

## 🧠 اختيار النموذج من الواجهة

**الموديلات المتاحة للصور:**
- ⚡ **Flux.1 Schnell** — سريع جداً ($0.003/صورة)
- 🎨 **Flux.1 Dev** — جودة عالية ($0.015/صورة)
- 🖼️ **SD3.5 Large Turbo** — دقيق (~$0.003)
- 🎭 **SDXL** — كلاسيكي ($0.005)

**الموديلات المتاحة للفيديو:**
- ⚡ **LTX-Video** — سريع ($0.02/فيديو)
- 🎬 **Mochi 1** — جودة عالية ($0.33/فيديو)
- 🎥 **Wan 2.1 14B** — ممتاز ($0.05)

## 🏗️ Architecture

```
[مستخدم] → [Gradio UI (VPS/Coolify/Modal)] → API → [Modal GPU Worker (H100)]
                (يدعم HTTPS + كلمة سر)                 (يدعم تبديل الموديلات)
```

## 🐳 النشر على Coolify

انظر [COOLIFY.md](./COOLIFY.md) للشرح الكامل.

**الخطوات السريعة:**
1. اربط ريبو GitHub `sdtrips/new` في Coolify
2. أضف Environment Variables: `API_URL`, `API_TOKEN`, `ADMIN_USER`, `ADMIN_PASS`
3. **Coolify يكتشف Dockerfile تلقائياً** 🎉

## 🔒 الأمان

- **طبقة 1:** Gradio Auth (كلمة سر للدخول)
- **طبقة 2:** API Token (بين الواجهة و GPU Worker)
- **طبقة 3:** HTTPS تلقائي من Coolify

## 🚀 النشر السريع

### 1. إعداد Modal
```bash
pip install modal
modal token new
modal secret create api-auth API_TOKEN=my-secret-key
```

### 2. رفع GPU Worker (يدعم كل الموديلات)
```bash
modal deploy modal-gpu-worker.py
```

### 3. تشغيل الواجهة
```bash
export API_URL="https://your-org--gpu-generator-image.modal.run"
export API_TOKEN="my-secret-key"
python vps-gradio-ui.py
# → http://localhost:7860
```
