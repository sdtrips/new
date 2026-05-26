# Serverless Media Generation Deployment 🎨🎬

نشر موديلات توليد الصور والفيديو مفتوحة المصدر على **Modal.com** باستخدام GPU سيرفرلس (تدفع فقط عند الاستخدام).

## 📋 الملفات

| الملف | الوصف |
|-------|-------|
| `modal-gpu-worker.py` | 🖥️ ملف GPU Worker — يشغل على H100 من Modal، يستقبل طلبات API ويولّد الصور/الفيديو |
| `vps-gradio-ui.py` | 🌐 واجهة Gradio تعمل على VPS (CPU only) — ترسل طلبات إلى الـ GPU Worker |
| `modal-gradio-ui.py` | ☁️ واجهة Gradio تعمل على Modal CPU (بدون VPS) |
| `PRICING.md` | 💰 أسعار GPUs المختلفة على Modal |
| `IMAGE-MODELS.md` | 🖼️ كتالوج موديلات توليد الصور |
| `VIDEO-MODELS.md` | 🎬 كتالوج موديلات توليد الفيديو |

## 🏗️ Architecture

```
[مستخدم] → [واجهة Gradio (VPS/Modal CPU)] → API → [Modal GPU Worker (H100)]
                (رخيص، دايم يعمل)                   (يشغل فقط عند الطلب)
```

## 🚀 النشر السريع

### 1. إعداد Modal
```bash
pip install modal
modal token new          # سجل الدخول
modal secret create api-auth API_TOKEN=secret-key
```

### 2. رفع GPU Worker
```bash
modal deploy modal-gpu-worker.py
# ↳ راح يظهر رابط API: https://your-org--gpu-generator-image.modal.run
```

### 3. تشغيل الواجهة
**على VPS:**
```bash
export API_URL="https://your-org--gpu-generator-image.modal.run"
export API_TOKEN="secret-key"
python vps-gradio-ui.py
```

**أو على Modal CPU:**
```bash
modal deploy modal-gradio-ui.py
```

## 💸 التكلفة (تقريبية)

| العملية | الوقت | التكلفة |
|---------|-------|---------|
| صورة Flux schnell | ~2 ثانية | ~$0.003 |
| فيديو LTX-Video (5 ثواني) | ~15 ثانية | ~$0.02 |
| صيانة الـ VPS شهرياً | — | ~$5–8 |

## 🔒 الأمان

- **Gradio Auth**: كلمة مرور للدخول للواجهة
- **API Token**: التوكن يمنع استخدام GPU من أشخاص غير مصرح لهم
- **Modal Secret**: التوكن مخزّن بشكل آمن في Modal

## 🧠 الموديلات المدعومة

**صور:** Flux.1-schnell, Flux.1-dev, SD3.5, SDXL
**فيديو:** LTX-Video, Mochi 1, Wan2.1, CogVideoX, HunyuanVideo
