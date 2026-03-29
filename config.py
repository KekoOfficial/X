import os

# =========================
# 🧠 BASE
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# =========================
# 📁 CARPETAS
# =========================
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")

# 📱 ANDROID GALERÍA
GALLERY_FOLDER = "/storage/emulated/0/Movies/MallyCuts"

# =========================
# 🌐 FLASK SERVER
# =========================
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# =========================
# 🤖 TELEGRAM BOT
# =========================
TELEGRAM_BOT_TOKEN = "PASTE_YOUR_TOKEN_HERE"
TELEGRAM_CHAT_ID = None

# =========================
# ⚙️ SISTEMA
# =========================
MAX_CONTENT_LENGTH = 1024 * 1024 * 500  # 500MB
ALLOWED_EXTENSIONS = {"mp4", "mov", "mkv", "avi"}

# =========================
# 🔧 INIT
# =========================
def ensure_folders():
    for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER, LOG_FOLDER, GALLERY_FOLDER]:
        os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS