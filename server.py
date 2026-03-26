from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, subprocess, math, datetime
from config import *

app = Flask(__name__)

# 🔥 Crear carpetas automáticamente
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)
os.makedirs(GALLERY_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

history = []

# 🎯 Obtener duración real del video
def get_duration(path):
    """Obtiene duración del video en segundos"""
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

# 🚀 Reparar MP4 incompleto
def fix_mp4(path):
    fixed = path.replace(".mp4","_fixed.mp4")
    subprocess.run([
        "ffmpeg","-y","-i",path,
        "-c","copy","-movflags","faststart",
        fixed
    ])
    return fixed

# 🚀 Corte automático perfecto
def cut_video(path, duration):
    total = get_duration(path)
    if total == 0:
        print("❌ Error leyendo duración del video, intentando reparar")
        path = fix_mp4(path)
        total = get_duration(path)
        if total == 0:
            print("❌ No se puede procesar el video")
            return

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

        print("▶ Ejecutando:", " ".join(cmd))
        subprocess.run(cmd)

        # 📱 Copiar a galería
        subprocess.run(["cp", output_download, output_gallery])

        # 📱 Actualizar galería Android
        subprocess.run([
            "am","broadcast",
            "-a","android.intent.action.MEDIA_SCANNER_SCAN_FILE",
            "-d", f"file://{output_gallery}"
        ])

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
        if not file:
            return "❌ No se subió archivo"

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        cut_video(path, duration)
        return redirect(url_for('history_page'))

    return render_template("upload_file.html")

# 🔗 DESCARGA POR LINK (yt-dlp)
@app.route('/link', methods=['GET','POST'])
def link_download():
    if request.method == 'POST':
        url = request.form['video_url']
        duration = int(request.form['duration'])
        temp = os.path.join(UPLOAD_FOLDER, "temp_video.mp4")

        print("⬇ Descargando video:", url)
        try:
            # Usar yt-dlp para cualquier página
            subprocess.run(["yt-dlp","-f","best[ext=mp4]",url,"-o",temp], check=True)
        except:
            return "❌ Error descargando el video"

        # Reparar MP4 y cortar
        fixed = fix_mp4(temp)
        cut_video(fixed, duration)

        return redirect(url_for('history_page'))

    return render_template("link_download.html")

# 📥 DESCARGAR ARCHIVO
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# 🚀 INICIO
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)