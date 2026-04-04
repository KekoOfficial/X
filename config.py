# config.py - MALLY CUTS v12
import os

# CREDENCIALES DE TELEGRAM
BOT_TOKEN = "TU_TOKEN_AQUI" # Reemplaza con el token de BotFather
CHAT_ID = -1003584710096    # ID del canal Mally Series [cite: -1003584710096]

# RUTAS DE DIRECTORIO
UPLOAD_FOLDER = "uploads"
DOWNLOAD_FOLDER = "downloads"

# CONFIGURACIÓN DEL SERVIDOR
HOST = "0.0.0.0"
PORT = 8000

def init_folders():
    """Garantiza que existan las carpetas necesarias para MallyCuts."""
    for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
