import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
log = Logger()
# Aumentamos a 10 hilos para permitir múltiples subidas simultáneas
executor = ThreadPoolExecutor(max_workers=10)

def upload_worker(p_path, filename, part_num, total, job_id):
    """Tarea dedicada a subir una parte lo más rápido posible."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        with open(p_path, 'rb') as v:
            res = requests.post(url, data={
                'chat_id': CHAT_ID,
                'caption': f"⚡ PARTE {part_num}/{total} | {filename}",
                'supports_streaming': True
            }, files={'video': v}, timeout=300)
        
        if res.status_code == 200:
            log.success(f"✅ Enviada parte {part_num}")
        os.remove(p_path)
    except Exception as e:
        log.error(f"❌ Error subiendo parte {part_num}: {e}")

def turbo_engine(input_path, filename):
    """Motor de segmentación reactiva."""
    base = os.path.splitext(filename)[0]
    # El comando genera partes y las numera
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        # 1. Corte ultra rápido (Stream Copy)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", "300",
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # 2. Detectar partes y lanzar subidas en paralelo inmediatamente
        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)
        
        log.info(f"🚀 Lanzando subida de {total} partes en paralelo...")
        
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            # Lanzamos cada parte a un hilo diferente para no esperar
            executor.submit(upload_worker, p_path, filename, i, total, "TURBO")

        # Limpiar original
        if os.path.exists(input_path): os.remove(input_path)

    except Exception as e:
        log.error(f"🔥 Fallo en el motor Turbo: {e}")

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/api/upload_pro", methods=["POST"])
def upload_pro():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400

    f_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, f"{f_id}_{file.filename}")
    file.save(path)

    # Iniciar motor en segundo plano
    executor.submit(turbo_engine, path, file.filename)
    
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
