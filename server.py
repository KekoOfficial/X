# server.py
from flask import Flask, render_template, request, redirect, url_for
import os
import subprocess
import urllib.request

app = Flask(__name__)

# Carpeta para uploads temporales
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Carpeta para logs
LOG_FOLDER = 'logs'
os.makedirs(LOG_FOLDER, exist_ok=True)

# Carpeta de vídeos cortados en galería
GALLERY_FOLDER = '/storage/emulated/0/Movies/MallyCuts'
os.makedirs(GALLERY_FOLDER, exist_ok=True)

# Historial de vídeos cortados
history = []

# Función para cortar vídeo usando FFmpeg
def cut_video_ffmpeg(input_path, chapters, duration):
    output_files = []
    for i in range(chapters):
        start_time = i * duration
        filename_base = os.path.splitext(os.path.basename(input_path))[0]
        output_filename = f"{filename_base}_part{i+1}.mp4"
        output_path = os.path.join(GALLERY_FOLDER, output_filename)
        
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

# Historial de vídeos cortados
@app.route('/history', methods=['GET', 'POST'])
def history_page():
    global history
    if request.method == 'POST':
        history = []
        return redirect(url_for('history_page'))
    return render_template('history.html', videos=history)

# Descargar vídeo desde link
@app.route('/link_download', methods=['GET', 'POST'])
def link_download():
    global history
    if request.method == 'POST':
        video_url = request.form['video_url']
        chapters = int(request.form['chapters'])
        duration = int(request.form['duration'])
        temp_path = os.path.join(UPLOAD_FOLDER, 'temp_video.mp4')
        
        # Descargar vídeo
        try:
            urllib.request.urlretrieve(video_url, temp_path)
        except Exception as e:
            with open(os.path.join(LOG_FOLDER, 'errors.log'), 'a') as f:
                f.write(f"Error descargando {video_url}: {str(e)}\n")
            return "Error descargando el vídeo"
        
        # Cortar vídeo
        files = cut_video_ffmpeg(temp_path, chapters, duration)
        history.append(f"Vídeo de {video_url} cortado en {chapters} capítulos de {duration}s")
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
            cut_video_ffmpeg(filepath, chapters, duration)
            history.append(f"Archivo {filename} cortado en {chapters} capítulos de {duration}s")
            return redirect(url_for('history_page'))
    return render_template('upload_file.html')

if __name__ == '__main__':
    app.run(debug=True)