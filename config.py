import os

# =========================
# 🔐 BOT / API SETTINGS
# =========================
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

# =========================
# 🌐 SERVER SETTINGS
# =========================
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# =========================
# 📁 BASE PATH
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")

# 📱 Android Gallery
GALLERY_FOLDER = "/storage/emulated/0/Download"

# =========================
# 🧠 AUTO SETUP FOLDERS
# =========================
def init_folders():
    folders = [
        UPLOAD_FOLDER,
        DOWNLOAD_FOLDER,
        LOG_FOLDER,
        GALLERY_FOLDER
    ]

    for f in folders:
        os.makedirs(f, exist_ok=True)