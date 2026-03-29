import os
import time
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify

from config import *

app = Flask(__name__)
init_folders()

CAPITULOS = 20


# =========================
# 🏠 HOME
# =========================
@app.route("/", methods=["GET"])
def index():
    return render_template("upload.html")


# =========================
# 📤 UPLOAD + SPLIT 20 CAPÍTULOS
# =========================
@app.route("/upload", methods=["POST"])
def upload():

    if "video" not in request.files:
        return "No file", 400

    file = request.files["video"]

    if file.filename == "":
        return "Empty file", 400

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    base = os.path.splitext(file.filename)[0]

    file.save(input_path)

    # 🔥 obtener duración real
    try:
        duration = float(subprocess.check_output([
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            input_path
        ]).decode().strip())
    except:
        return "Error leyendo video", 500

    segment_time = duration / CAPITULOS

    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_cap_%02d.mp4")

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c", "copy",
        "-f", "segment",
        "-segment_time", str(segment_time),
        "-reset_timestamps", "1",
        output_pattern
    ]

    start = time.time()
    subprocess.run(cmd)
    end = time.time()

    return render_template("done.html", base=base, time=round(end-start, 2))


# =========================
# 📜 HISTORY
# =========================
@app.route("/history")
def history():

    files = os.listdir(DOWNLOAD_FOLDER)

    return render_template("history.html", videos=files)


# =========================
# 📥 DOWNLOAD
# =========================
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


# =========================
# 📊 STATUS
# =========================
@app.route("/status")
def status():
    return jsonify({"status": "online"})


# =========================
# 🚀 RUN
# =========================
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)