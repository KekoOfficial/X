import os
import time
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify

from config import *
from logger import Logger

# =========================
# INIT
# =========================
app = Flask(__name__)
init_folders()

log = Logger("MallyCuts")

# =========================
# 🏠 HOME
# =========================
@app.route("/")
def index():
    return render_template("upload_file.html")

# =========================
# 📤 UPLOAD + CUT VIDEO
# =========================
@app.route("/upload", methods=["POST"])
def upload():

    if "video_file" not in request.files:
        return "No file uploaded"

    file = request.files["video_file"]
    duration = request.form.get("duration", "5")

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_name = "cut_" + file.filename
    output_path = os.path.join(DOWNLOAD_FOLDER, output_name)

    file.save(input_path)

    # =========================
    # 🎬 FFMPEG COMMAND (PRO FIXED)
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

    # =========================
    # 📄 LOG OUTPUT
    # =========================
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
@app.route("/history")
def history_page():

    files = []

    if os.path.exists(DOWNLOAD_FOLDER):
        for f in os.listdir(DOWNLOAD_FOLDER):
            path = os.path.join(DOWNLOAD_FOLDER, f)

            files.append({
                "name": f,
                "size": round(os.path.getsize(path) / 1024, 2)
            })

    return render_template("history.html", videos=files)

# =========================
# 📥 DOWNLOAD FILE
# =========================
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# =========================
# 📊 API STATUS (BOT / WEB)
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
    print(f"Running on http://{HOST}:{PORT}")

    app.run(
        host=HOST,
        port=PORT,
        debug=DEBUG
    )