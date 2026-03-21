from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, subprocess, math, datetime, glob
from config import *

app = Flask(__name__)

# 🔥 Crear carpetas automáticamente
for folder in [UPLOAD_FOLDER, DOWNLOAD_FOLDER, LOG_FOLDER, GALLERY_FOLDER]:
    os.makedirs(folder, exist_ok=True)

history = []

# 🎯 Obtener duración real del video
def get_duration(path):
    try:
        result = subprocess.run([
            "ffprobe","-v","error",
            "-show_entries","format=duration",
            "-of","default=noprint_wrappers=1:nokey=1",
            path
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return float(result.stdout)
    except:
        return 0

# 🎨 Extraer miniatura
def generate_thumbnail(path):
    base = os.path.splitext(os.path.basename(path))[0]
    thumb_path = os.path.join(DOWNLOAD_FOLDER, f"{base}_thumb.jpg")
    cmd = [
        "ffmpeg","-y","-i",path,
        "-ss","00:00:01","-vframes","1",
        thumb_path
    ]
    subprocess.run(cmd)
    return thumb_path

# 🚀 Corte automático preciso
def cut_video(path, duration, rename=True):
    total = get_duration(path)
    if total == 0:
        print("❌ Error leyendo duración del video")
        return

    parts = math.ceil(total / duration)
    name = os.path.splitext(os.path.basename(path))[0]

    for i in range(parts):
        start = i * duration
        output_name = f"{name}_{i+1:02}.mp4" if rename else f"{name} #{i+1}.mp4"
        out_download = os.path.join(DOWNLOAD_FOLDER, output_name)
        out_gallery = os.path.join(GALLERY_FOLDER, output_name)

        cmd = ["ffmpeg","-y","-ss",str(start),"-i",path,"-t",str(duration),"-c","copy",out_download]
        subprocess.run(cmd)

        # Copiar a galería
        subprocess.run(["cp", out_download, out_gallery])
        subprocess.run(["am","broadcast","-a","android.intent.action.MEDIA_SCANNER_SCAN_FILE","-d",f"file://{out_gallery}"])

    # Limpiar temporales
    if path.startswith(UPLOAD_FOLDER):
        try: os.remove(path)
        except: pass

    # Guardar en historial
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
        thumb = generate_thumbnail(path)
        cut_video(path, duration)
        return redirect(url_for('history_page'))
    return render_template("upload_file.html")

# 🔗 LINK (yt-dlp)
@app.route('/link', methods=['GET','POST'])
def link_download():
    if request.method == 'POST':
        url = request.form['video_url']
        duration = int(request.form['duration'])
        temp = os.path.join(UPLOAD_FOLDER, "temp_video.mp4")

        # Descargar con yt-dlp
        try:
            subprocess.run(["yt-dlp","-f","best[ext=mp4]",url,"-o",temp])
        except Exception as e:
            return f"❌ Error descargando: {e}"

        thumb = generate_thumbnail(temp)
        cut_video(temp, duration)
        return redirect(url_for('history_page'))

    return render_template("link_download.html")

# 📥 DESCARGAR ARCHIVO
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# 🔥 LIMPIAR DOWNLOADS
@app.route('/clear_downloads')
def clear_downloads():
    files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*"))
    for f in files: os.remove(f)
    return redirect(url_for('history_page'))

# 🚀 INICIO
if __name__ == "__main__":
    print("💻 Servidor iniciado en http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)