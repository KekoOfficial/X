# server.py
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess
import yt_dlp
from datetime import datetime

app = Flask(__name__)

# Carpetas necesarias
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'Downloads'
LOG_FOLDER = 'logs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# Historial (temporal, puedes cambiar a base de datos si quieres)
history = []

# Función para cortar vídeo con FFmpeg en capítulos exactos
def cut_video_ffmpeg(input_path, chapters, duration):
    output_files = []
    for i in range(chapters):
        start_time = i * duration
        output_filename = f"{os.path.splitext(os.path.basename(input_path))[0]}_part{i+1}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)

        # Comando FFmpeg
        cmd = [
            'ffmpeg', '-y', '-i', input_path,
            '-ss', str(start_time),
            '-t', str(duration),
            '-c', 'copy',
            output_path
        ]

        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            output_files.append(output_filename)
        except subprocess.CalledProcessError:
            with open(os.path.join(LOG_FOLDER, 'errors.log'), 'a') as f:
                f.write(f"Error cortando {input_path} capítulo {i+1}\n")
    return output_files

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# Historial
@app.route('/history', methods=['GET', 'POST'])
def history_page():
    global history
    if request.method == 'POST':
        history = []  # Borrar historial
        return redirect(url_for('history_page'))
    return render_template('history.html', videos=history)

# Descargar y cortar desde link
@app.route('/link_download', methods=['GET', 'POST'])
def link_download():
    global history
    if request.method == 'POST':
        video_url = request.form['video_url']
        chapters = int(request.form['chapters'])
        duration = int(request.form['duration'])

        # Archivo temporal
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        temp_video_path = os.path.join(UPLOAD_FOLDER, f"temp_{timestamp}.mp4")

        # Descargar vídeo real
        ydl_opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': temp_video_path,
            'quiet': True,
            'merge_output_format': 'mp4'
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            history.append(f"Error descargando {video_url}: {str(e)}")
            return redirect(url_for('history_page'))

        # Cortar vídeo
        output_files = cut_video_ffmpeg(temp_video_path, chapters, duration)
        history.append(f"Vídeo {video_url} cortado: {', '.join(output_files)}")

        # Limpiar temporal
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

        return redirect(url_for('history_page'))
    return render_template('link_download.html')

# Subir archivo y cortar
@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    global history
    if request.method == 'POST':
        file = request.files['video_file']
        chapters = int(request.form['chapters'])
        duration = int(request.form['duration'])
        if file:
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)

            # Cortar vídeo
            output_files = cut_video_ffmpeg(filepath, chapters, duration)
            history.append(f"Archivo {filename} cortado: {', '.join(output_files)}")

            # Opcional: borrar archivo subido después de cortar
            os.remove(filepath)

            return redirect(url_for('history_page'))
    return render_template('upload_file.html')

# Descargar capítulo específico
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)