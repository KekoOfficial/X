import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "Downloads")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")

# 📱 Carpeta real de galería Android
GALLERY_FOLDER = "/storage/emulated/0/Movies/MallyCuts"