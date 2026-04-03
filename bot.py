import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

# 1. DEFINICIÓN DEL APP (Esto arregla tu error)
app = Flask(__name__)
log = Logger()
executor = ThreadPoolExecutor(max_workers=5)

# ==========================================
# ⚙️ MOTOR TURBO-SYNC (Punto 4 Integrado)
# ==========================================

def synchronized_engine(input_path, filename, segment_time, silent_mode):
    """Motor Pro con tiempo dinámico y modo silencio."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        # Corte instantáneo con el tiempo recibido (60, 300 o 600)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", str(segment_time),
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)

        # Envío secuencial para orden perfecto
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            with open(p_path, 'rb') as v:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                    'chat_id': CHAT_ID,
                    'caption': f"📦 PARTE {i}/{total}\n🎬 {filename}\n⚡ MallyCuts Sync",
                    'supports_streaming': True,
                    'disable_notification': silent_mode # Soporte para Modo Silencio
                }, files={'video': v}, timeout=300)
            
            os.remove(p_path) # Limpieza inmediata
            time.sleep(1.2) # Pausa de sincronía

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"✅ Proceso terminado: {total} partes enviadas.")

    except Exception as e:
        log.error(f"🔥 Error en motor: {e}")

# ==========================================
# 🌐 RUTAS DE CONTROL
# ==========================================

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/api/upload_pro", methods=["POST"])
def upload_pro():
    file = request.files.get("video")
    # Captura de datos dinámicos del formulario
    sec = int(request.form.get("seconds", 60))
    silent = request.form.get("silent") == "true"

    if not file: return jsonify({"status": "error"}), 400

    f_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, f"{f_id}_{file.filename}")
    file.save(path)

    # Disparo asíncrono con los nuevos parámetros
    executor.submit(synchronized_engine, path, file.filename, sec, silent)
    
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
