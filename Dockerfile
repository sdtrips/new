# 🐳 Dockerfile for Gradio UI — deploy on Coolify or any Docker host
#
# Architecture: [User] → Coolify (this container) → Modal GPU Worker
#                                              ↕ HTTPS + API Token
#
# Usage with Coolify:
#   1. Connect your GitHub repo (sdtrips/new)
#   2. Coolify auto-detects this Dockerfile
#   3. Set Environment Variables in Coolify dashboard:
#      - API_URL (required): URL of your deployed Modal GPU Worker for images
#      - API_VIDEO_URL (required): URL for video endpoint
#      - API_TOKEN (required): Secret token shared with GPU Worker
#      - ADMIN_USER: Login username (default: admin)
#      - ADMIN_PASS: Login password (default: mypassword123 — CHANGE IT!)
#   4. Deploy 🚀
#
# Security layers:
#   🔐 Layer 1: Gradio Auth (username + password at login)
#   🔐 Layer 2: API Token (between UI and Modal GPU Worker)
#   🔐 Layer 3: Coolify HTTPS (automatically provided)

FROM python:3.12-slim

WORKDIR /app

# Install only what Gradio UI needs — no torch, no GPU libs
COPY requirements-ui.txt .
RUN pip install --no-cache-dir -r requirements-ui.txt

# Copy the UI code
COPY vps-gradio-ui.py .

# Default port for Gradio
EXPOSE 7860

# Run the UI
CMD ["python", "vps-gradio-ui.py"]
