import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DOWNLOAD_FOLDER = os.path.join(BASE_DIR, "Downloads")
THUMBNAILS_FOLDER = os.path.join(BASE_DIR, "thumbnails")
LOGS_FOLDER = os.path.join(BASE_DIR, "logs")
TEMP_FOLDER = os.path.join(BASE_DIR, "temp")

# Duración por capítulo en segundos
CHAPTER_DURATION = 15

# Crear carpetas si no existen
for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER, THUMBNAILS_FOLDER, LOGS_FOLDER, TEMP_FOLDER]:
    os.makedirs(folder, exist_ok=True)