from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, subprocess, math, datetime

from config import *

# =========================
# 🚀 INIT
# =========================
app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

ensure_folders()

# 📜 HISTORIAL GLOBAL
history = []

# =========================
# 🎯 VIDEO UTILS
# =========================
def get_duration(path):
    result = subprocess.run([
        "ffprobe","-v","error",
        "-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",
        path
    ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    try:
        return float(result.stdout)
    except:
        return 0


def fix_mp4(path):
    fixed = path.replace(".mp4", "_fixed.mp4")
    subprocess.run([
        "ffmpeg","-y","-i",path,
        "-c","copy","-movflags","faststart",
        fixed
    ])
    return fixed


def cut_video(path, duration):
    total = get_duration(path)

    if total == 0:
        path = fix_mp4(path)
        total = get_duration(path)
        if total == 0:
            return

    parts = math.ceil(total / duration)
    name = os.path.splitext(os.path.basename(path))[0]

    files = []

    for i in range(parts):
        start = i * duration
        output_name = f"{name}_cap_{i+1}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_name)

        subprocess.run([
            "ffmpeg","-y",
            "-ss", str(start),
            "-i", path,
            "-t", str(duration),
            "-c","copy",
            output_path
        ])

        files.append(output_name)

    history.append({
        "name": name,
        "clips": files,
        "date": str(datetime.datetime.now())
    })

# =========================
# 🏠 HOME
# =========================
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':

        file = request.files.get('video_file')
        if not file or file.filename == "":
            return "❌ Archivo inválido", 400

        if not allowed_file(file.filename):
            return "❌ Formato no permitido", 400

        try:
            duration = int(request.form.get('duration', 0))
        except:
            return "❌ Duración inválida", 400

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        cut_video(path, duration)

        return redirect(url_for('history_page'))

    return render_template("upload_file.html")

# =========================
# 📜 HISTORY
# =========================
@app.route('/history')
def history_page():
    return render_template("history.html", videos=history)

# =========================
# 📥 DOWNLOAD FILE
# =========================
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# =========================
# 🚀 START SERVER
# =========================
if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=DEBUG)