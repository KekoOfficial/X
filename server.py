import os
import uuid
import time
import threading
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify

from config import *

app = Flask(__name__)
init_folders()

CAPITULOS = 20

# =========================
# 📊 MEMORY JOBS (estado)
# =========================
JOBS = {}


# =========================
# 🏠 HOME
# =========================
@app.route("/")
def index():
    return render_template("upload.html")


# =========================
# 📤 UPLOAD (NO BLOQUEA)
# =========================
@app.route("/upload", methods=["POST"])
def upload():

    file = request.files.get("video")

    if not file:
        return "No file", 400

    job_id = str(uuid.uuid4())[:8]

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    JOBS[job_id] = {
        "status": "processing",
        "progress": 0,
        "file": file.filename
    }

    thread = threading.Thread(
        target=process_video,
        args=(job_id, input_path, file.filename)
    )
    thread.start()

    return render_template("processing.html", job_id=job_id)


# =========================
# ⚙️ PROCESO EN BACKGROUND
# =========================
def process_video(job_id, input_path, filename):

    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_cap_%02d.mp4")

    try:
        # 📏 duración
        duration = float(subprocess.check_output([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ]).decode().strip())

        segment_time = duration / CAPITULOS

        JOBS[job_id]["progress"] = 20

        cmd = [
            "ffmpeg", "-y",
            "-i", input_path,
            "-c", "copy",
            "-f", "segment",
            "-segment_time", str(segment_time),
            "-reset_timestamps", "1",
            output_pattern
        ]

        subprocess.run(cmd)

        JOBS[job_id]["status"] = "done"
        JOBS[job_id]["progress"] = 100

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)


# =========================
# 📊 PROGRESS API
# =========================
@app.route("/progress/<job_id>")
def progress(job_id):

    job = JOBS.get(job_id)

    if not job:
        return jsonify({"status": "not_found"})

    return jsonify(job)


# =========================
# 📜 HISTORY
# =========================
@app.route("/history")
def history():

    files = []

    if os.path.exists(DOWNLOAD_FOLDER):
        files = sorted(os.listdir(DOWNLOAD_FOLDER), reverse=True)

    return render_template("history.html", videos=files)


# =========================
# 📥 DOWNLOAD
# =========================
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


# =========================
# 📊 STATUS GENERAL
# =========================
@app.route("/status")
def status():
    return jsonify({
        "status": "online",
        "jobs": len(JOBS),
        "caps": CAPITULOS
    })


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG,
        threaded=True
    )