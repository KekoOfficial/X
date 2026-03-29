from flask import Flask, request, render_template, send_from_directory
import subprocess
import time

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
    file = request.files["video_file"]
    duration = request.form.get("duration")

    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(DOWNLOAD_FOLDER, "cut_" + file.filename)

    file.save(input_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-t", str(duration),
        "-c:v", "copy",
        "-c:a", "aac",
        output_path
    ]

    start = time.time()

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    _, stderr = process.communicate()

    end = time.time()

    ff_log = log.ffmpeg(end-start, process.returncode, stderr)

    print(ff_log)

    return ff_log

# =========================
# 📥 DOWNLOAD FILES
# =========================
@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

# =========================
# 🚀 RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)