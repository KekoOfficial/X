from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, subprocess, math, datetime
from config import *

app = Flask(__name__)

# Crear carpetas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)

history = []

# 🔥 Duración del video
def get_duration(path):
    result = subprocess.run([
        "ffprobe","-v","error",
        "-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",
        path
    ], stdout=subprocess.PIPE)
    return float(result.stdout)

# 🚀 Corte automático
def cut_video(path, duration):
    total = get_duration(path)
    parts = math.ceil(total / duration)

    name = os.path.splitext(os.path.basename(path))[0]

    for i in range(parts):
        start = i * duration

        output_name = f"{name} #{i+1}.mp4"
        output_download = os.path.join(DOWNLOAD_FOLDER, output_name)
        output_gallery = os.path.join(GALLERY_FOLDER, output_name)

        cmd = [
            "ffmpeg","-y",
            "-ss", str(start),
            "-i", path,
            "-t", str(duration),
            "-c","copy",
            output_download
        ]

        subprocess.run(cmd)

        # Copiar a galería
        subprocess.run(["cp", output_download, output_gallery])

    history.append({
        "name": name,
        "clips": parts,
        "date": str(datetime.datetime.now())
    })

# 🏠 HOME
@app.route('/')
def index():
    return render_template("index.html")

# 📜 HISTORIAL
@app.route('/history', methods=['GET','POST'])
def history_page():
    global history
    if request.method == 'POST':
        history = []
    return render_template("history.html", videos=history)

# 📁 SUBIR ARCHIVO
@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['video_file']
        duration = int(request.form['duration'])

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        cut_video(path, duration)

        return redirect(url_for('history_page'))

    return render_template("upload_file.html")

# 🔗 LINK
@app.route('/link', methods=['GET','POST'])
def link_download():
    if request.method == 'POST':
        url = request.form['video_url']
        duration = int(request.form['duration'])

        temp = os.path.join(UPLOAD_FOLDER, "temp.mp4")

        subprocess.run(["wget", url, "-O", temp])

        cut_video(temp, duration)

        return redirect(url_for('history_page'))

    return render_template("link_download.html")

# 📥 DESCARGA
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)