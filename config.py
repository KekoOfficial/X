import os

# =========================
# 🔐 CREDENCIALES
# =========================
BOT_TOKEN = "TU_BOT_TOKEN_AQUI"
CHAT_ID = "TU_CHAT_ID_AQUI" # Tu ID numérico

# =========================
# 🌐 RED
# =========================
HOST = "0.0.0.0"
PORT = 8000
DEBUG = False # En producción mejor False

# =========================
# 📁 SISTEMA DE ARCHIVOS
# =========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "downloads")

def init_folders():
    for f in [UPLOAD_FOLDER, DOWNLOAD_FOLDER]:
        if not os.path.exists(f):
            os.makedirs(f, exist_ok=True)
