# 🚀 نشر الواجهة على Coolify

## المتطلبات
- حساب Coolify (أو Coolify مثبت على السيرفر)
- ريبو GitHub `sdtrips/new`
- Modal GPU Worker منشور (`modal deploy modal-gpu-worker.py`)

## ⚡ النشر

### 1. أضف Environment Variables في Coolify
في إعدادات المشروع → Environment Variables، أضف:

| المتغير | الوصف | مثال |
|---------|-------|------|
| `API_URL` | رابط API الصور (من Modal deploy) | `https://your-org--gpu-generator-image.modal.run` |
| `API_VIDEO_URL` | رابط API الفيديو | `https://your-org--gpu-generator-video.modal.run` |
| `API_TOKEN` | التوكن السري (نفس اللي في Modal) | `my-secret-key` |
| `ADMIN_USER` | اسم المستخدم (اختياري) | `admin` |
| `ADMIN_PASS` | 🔑 **كلمة سر قوية!** | `P@ssw0rd!2026` |

### 2. اضبط Domain
- Coolify يوفر HTTPS تلقائي
- استخدم domain: `video.yourdomain.com` (أو أي اسم)

### 3. نشر
- Coolify يبني الـ Dockerfile ويرفع الصورة
- أول نشر: ~30-60 ثانية
- التحديثات: ~5-10 ثواني

## 🔒 الأمان (طبقتين)

```
الويب (HTTPS)
    ↓  ← Layer 1: Gradio Auth (ADMIN_USER + ADMIN_PASS)
واجهة Gradio
    ↓  ← Layer 2: API Token (x-api-token header)
Modal GPU Worker
```

### Layer 1: Gradio Auth
المستخدم يكتب **اسم مستخدم + كلمة سر** عند أول دخول.
Gradio يعطي **cookie** للجلسة — ما يطلب تسجيل الدخول مرة ثانية لنفس المتصفح.

### Layer 2: API Token
حتى لو أحد اخترق Domain ما يقدر يستخدم GPU Worker بدون التوكن.
API_TOKEN مخزّن في Environment Variable — مو مكتوب في الكود.

## 💰 التكلفة مع Coolify

| العنصر | التكلفة |
|--------|---------|
| Coolify نفسه | مجاني (Open Source) |
| VPS لـ Coolify | ~$5-10/شهر (Hetzner, DigitalOcean) |
| Modal GPU | فقط وقت التوليد (~$0.003/صورة) |
| **المجموع** | **~$5-10/شهر + استخدام GPU** |
