import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "Downloads")
THUMB_FOLDER = os.path.join(BASE_DIR, "thumbnails")
LOG_FOLDER = os.path.join(BASE_DIR, "logs")

# Duración por capítulo en segundos
CHAPTER_DURATION = 15

# Extensiones válidas
ALLOWED_EXTENSIONS = {'mp4', 'mov', 'mkv', 'avi'}