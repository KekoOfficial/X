# config.py - MALLY NEXUS v13
import os, json

DB_PATH = "database/settings.json"
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"

def get_nexus_settings():
    """Lee los tokens de la base de datos local sin exponerlos en el código."""
    if not os.path.exists(DB_PATH):
        return {"bot_token": None, "chat_id": None}
    with open(DB_PATH, "r") as f:
        return json.load(f)

def init_nexus():
    """Prepara las carpetas de la Consola."""
    for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER, "database"]:
        if not os.path.exists(folder):
            os.makedirs(folder)
