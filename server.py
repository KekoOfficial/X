from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
import subprocess
import math

app = Flask(__name__)

# Carpetas
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'Downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Historial simple en memoria
history = []

# Función para cortar vídeos usando ffmpeg
def cut_video_ffmpeg(filepath, chapters, duration):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    output_files = []

    for i in range(chapters):
        start_time = i * duration
        output_name = f"{name}_chapter{i+1}{ext}"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_name)
        # ffmpeg sin re-encode para rapidez
        subprocess.run([
            "ffmpeg",
            "-y",  # Sobrescribir si existe
            "-i", filepath,
            "-ss", str(start_time),
            "-t", str(duration),
            "-c", "copy",
            output_path
        ])
        output_files.append(output_name)
    return output_files

# Rutas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/history', methods=['GET', 'POST'])
def history_page():
    global history
    if request.method == 'POST':
        history = []
        return redirect(url_for('history_page'))
    return render_template('history.html', videos=history)

@app.route('/link_download', methods=['GET', 'POST'])
def link_download():
    global history
    if request.method == 'POST':
        video_url = request.form['video_url']
        chapters = int(request.form['chapters'])
        duration = int(request.form['duration'])
        # Aquí podrías usar yt-dlp o youtube-dl para descargar el vídeo primero
        # Por ahora simulamos
        fake_file = os.path.join(UPLOAD_FOLDER, "temp_video.mp4")
        open(fake_file, "a").close()  # Archivo vacío de prueba
        output_files = cut_video_ffmpeg(fake_file, chapters, duration)
        history.append(f"Vídeo de {video_url} cortado: {', '.join(output_files)}")
        return redirect(url_for('history_page'))
    return render_template('link_download.html')

@app.route('/upload_file', methods=['GET', 'POST'])
def upload_file():
    global history
    if request.method == 'POST':
        file = request.files['video_file']
        chapters = int(request.form['chapters'])
        duration = int(request.form['duration'])
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)
            output_files = cut_video_ffmpeg(filepath, chapters, duration)
            history.append(f"Archivo {file.filename} cortado: {', '.join(output_files)}")
            return redirect(url_for('history_page'))
    return render_template('upload_file.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)