import os

# Ruta raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Directorios de la Empresa
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
DOWNLOADS_DIR = os.path.join(BASE_DIR, "downloads")
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DB_PATH = os.path.join(BASE_DIR, "database", "db.sqlite3")

# Asegurar existencia de carpetas críticas
for folder in [UPLOADS_DIR, DOWNLOADS_DIR, LOGS_DIR]:
    os.makedirs(folder, exist_ok=True)
