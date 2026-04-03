import os
import uuid
import time
import threading
import subprocess
import requests
from flask import Flask, request, render_template, jsonify
from config import *
from logger import Logger

app = Flask(__name__)
log = Logger()
init_folders()

# Estado de los trabajos en tiempo real
JOBS = {}

def enviar_clip(file_path, num, job_id):
    """Envía el video y lo elimina inmediatamente del storage."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        with open(file_path, 'rb') as v:
            data = {'chat_id': CHAT_ID, 'caption': f"📦 Parte {num}\n🆔 {job_id}"}
            res = requests.post(url, data=data, files={'video': v})
            if res.status_code == 200:
                log.success(f"Parte {num} enviada.")
                os.remove(file_path) # 🔥 LIMPIEZA TOTAL
            else:
                log.error(f"Telegram rechazó parte {num}")
    except Exception as e:
        log.error(f"Fallo en envío: {e}")

def engine_processor(job_id, input_path, filename, seconds):
    start_time = time.time()
    base = os.path.splitext(filename)[0]
    # Patrón de salida: downloads/video_cap_001.mp4
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_cap_%03d.mp4")

    try:
        log.info(f"Iniciando corte de {filename} cada {seconds}s")
        
        # Comando FFmpeg avanzado: segmentación rápida por tiempo
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-f", "segment",
            "-segment_time", str(seconds),
            "-reset_timestamps", "1", output_pattern
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)

        # Escanear capítulos creados
        clips = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        
        for i, clip_name in enumerate(clips, 1):
            clip_path = os.path.join(DOWNLOAD_FOLDER, clip_name)
            enviar_clip(clip_path, i, job_id)

        JOBS[job_id]["status"] = "done"
        log.ffmpeg_report(job_id, time.time() - start_time)
        
        # Borrar el video original subido
        if os.path.exists(input_path): os.remove(input_path)

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
        log.error(f"Error en Job {job_id}: {e}")

@app.route("/")
def home():
    return render_template("upload.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("video")
    t_choice = int(request.form.get("time_choice", 300))

    if not file: return "Error", 400

    job_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    JOBS[job_id] = {"status": "processing"}
    
    # Hilo separado para no bloquear la web
    threading.Thread(target=engine_processor, args=(job_id, path, file.filename, t_choice)).start()
    
    return render_template("progress.html", job_id=job_id)

@app.route("/progress/<job_id>")
def progress(job_id):
    return jsonify(JOBS.get(job_id, {"status": "not_found"}))

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
