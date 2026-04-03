import os
import uuid
import threading
import subprocess
import requests
import json
from flask import Flask, request, render_template, jsonify
from config import *
from logger import Logger

app = Flask(__name__)
log = Logger()
init_folders()

TEMP_FILES = {} # Almacena datos temporales antes de confirmar

def get_video_duration(file_path):
    """Usa ffprobe para obtener la duración exacta en segundos."""
    cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", file_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return float(result.stdout) if result.stdout else 0

def engine_processor(job_id, input_path, filename, seconds):
    """Procesador que solo arranca cuando tú confirmas."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_cap_%03d.mp4")

    try:
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-f", "segment",
            "-segment_time", str(seconds),
            "-reset_timestamps", "1", output_pattern
        ]
        subprocess.run(cmd, check=True)

        clips = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        for i, clip_name in enumerate(clips, 1):
            enviar_clip(os.path.join(DOWNLOAD_FOLDER, clip_name), i, job_id)

        if os.path.exists(input_path): os.remove(input_path)
    except Exception as e:
        log.error(f"Error: {e}")

@app.route("/")
def home():
    return render_template("upload.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    """Ruta nueva: Recibe el video, lo analiza y te da opciones."""
    file = request.files.get("video")
    if not file: return "No file", 400

    file_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(path)

    duration = get_video_duration(path)
    
    # Cálculos de capítulos
    opciones = {
        "3min": {"seg": 180, "caps": int(duration // 180) + 1},
        "5min": {"seg": 300, "caps": int(duration // 300) + 1},
        "10min": {"seg": 600, "caps": int(duration // 600) + 1}
    }

    TEMP_FILES[file_id] = {"path": path, "name": file.filename, "duration": duration}

    return jsonify({
        "file_id": file_id,
        "name": file.filename,
        "duration_msg": f"{round(duration/60, 2)} minutos",
        "options": opciones
    })

@app.route("/confirm", methods=["POST"])
def confirm():
    """Ruta nueva: Aquí es donde realmente empieza el corte."""
    data = request.json
    f_id = data.get("file_id")
    seconds = int(data.get("seconds"))

    if f_id in TEMP_FILES:
        video_data = TEMP_FILES[f_id]
        job_id = f_id
        threading.Thread(target=engine_processor, args=(job_id, video_data["path"], video_data["name"], seconds)).start()
        return jsonify({"status": "started", "job_id": job_id})
    
    return "Error", 400

# (Mantén las rutas de /progress y la función enviar_clip que ya tienes)
