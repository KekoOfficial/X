import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Carpetas del Sistema
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

# Crear carpetas si no existen
for d in [UPLOADS_DIR, DOWNLOADS_DIR, DATABASE_DIR]:
    os.makedirs(d, exist_ok=True)
