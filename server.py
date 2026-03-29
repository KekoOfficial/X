import os
import time
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify

from config import *
from logger import Logger

# =========================
# INIT APP
# =========================
app = Flask(__name__)
init_folders()

log = Logger("MallyCuts")

# =========================
# 🏠 HOME (SOLO GET)
# =========================
@app.route("/", methods=["GET"])
def index():
    return render_template("upload_file.html")

# =========================
# 📤 UPLOAD + CUT VIDEO
# =========================
@app.route("/upload", methods=["POST"])
def upload():

    # VALIDACIÓN FILE
    if "video_file" not in request.files:
        return "❌ No file uploaded", 400

    file = request.files["video_file"]
    duration = request.form.get("duration", "5")

    if file.filename == "":
        return "❌ Empty filename", 400

    # PATHS
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_name = "cut_" + file.filename
    output_path = os.path.join(DOWNLOAD_FOLDER, output_name)

    file.save(input_path)

    # =========================
    # 🎬 FFMPEG (STABLE MODE)
    # =========================
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "128k",
        output_path
    ]

    start = time.time()

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    _, stderr = process.communicate()

    end = time.time()

    # LOG
    ff_log = log.ffmpeg(
        process_time=end - start,
        return_code=process.returncode,
        raw=stderr
    )

    print(ff_log)

    return ff_log

# =========================
# 📜 HISTORY (FIXED)
# =========================
@app.route("/history", methods=["GET"])
def history_page():

    videos = []

    if os.path.exists(DOWNLOAD_FOLDER):
        for f in os.listdir(DOWNLOAD_FOLDER):
            path = os.path.join(DOWNLOAD_FOLDER, f)

            if os.path.isfile(path):
                videos.append({
                    "name": f,
                    "size_kb": round(os.path.getsize(path) / 1024, 2)
                })

    return render_template("history.html", videos=videos)

# =========================
# 📥 DOWNLOAD FILE
# =========================
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(
        DOWNLOAD_FOLDER,
        filename,
        as_attachment=True
    )

# =========================
# 📊 STATUS API (BOT + WEB)
# =========================
@app.route("/status")
def status():
    return jsonify({
        "status": "online",
        "service": "MallyCuts",
        "time": time.time()
    })

# =========================
# 🚀 RUN SERVER
# =========================
if __name__ == "__main__":
    print(log.success("Server starting..."))
    print(f"🌐 Running on http://{HOST}:{PORT}")

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )