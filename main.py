import os, uuid, json
from flask import Flask, render_template, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import init_nexus, DB_PATH
from bot import start_mally_engine
from logger import Logger

app = Flask(__name__)
log = Logger()
# 10 hilos para procesar múltiples series en paralelo
executor = ThreadPoolExecutor(max_workers=10)

# --- RUTAS DE NAVEGACIÓN ---

@app.route("/")
def index():
    """Panel de Control Principal (Subida)"""
    return render_template("upload.html")

@app.route("/settings")
def settings_page():
    """Panel Privado de Configuración de Tokens"""
    return render_template("settings.html")

# --- API DE OPERACIONES ---

@app.route("/api/save_settings", methods=["POST"])
def save_settings():
    """Guarda los tokens en database/settings.json"""
    try:
        data = request.json
        os.makedirs("database", exist_ok=True)
        with open(DB_PATH, "w") as f:
            json.dump(data, f)
        log.success("Base de Datos NEXUS Actualizada.")
        return jsonify({"status": "success"})
    except Exception as e:
        log.error(f"Error guardando ajustes: {e}")
        return jsonify({"status": "error"}), 500

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    """Recibe el video e inicia el Motor Mally"""
    file = request.files.get("video")
    if not file:
        return jsonify({"status": "error", "message": "No hay archivo"}), 400
    
    # Nombre único para evitar conflictos en carpetas públicas
    path = os.path.join("uploads", f"V13_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    
    log.info(f"⚡ Consola: Procesando {file.filename}")
    # Ejecución en segundo plano para no bloquear la web
    executor.submit(start_mally_engine, path, file.filename)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_nexus()
    log.info("🛡️ MALLY NEXUS v13 - KHASSAMX DEV ONLINE")
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
