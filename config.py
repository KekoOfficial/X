import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_DIR = os.path.join(BASE_DIR, "database")
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
DB_PATH = os.path.join(DATABASE_DIR, "config.json")

# Asegurar que existan las carpetas
for folder in [DATABASE_DIR, UPLOADS_DIR, DOWNLOADS_DIR]:
    os.makedirs(folder, exist_ok=True)
