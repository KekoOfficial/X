from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
import os
from datetime import datetime
from moviepy.editor import VideoFileClip

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Para flash messages

# Carpetas
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'Downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Historial de vídeos cortados
history = []

# Función para cortar vídeo en capítulos
def cut_video(filepath, chapters, duration_per_chapter):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    clip = VideoFileClip(filepath)
    total_duration = int(clip.duration)
    output_files = []

    # Cortar vídeo en capítulos
    start = 0
    chapter_num = 1
    while start < total_duration and chapter_num <= chapters:
        end = min(start + duration_per_chapter, total_duration)
        output_filename = f"{name}_chapter{chapter_num}{ext}"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_filename)
        clip.subclip(start, end).write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        output_files.append(output_filename)
        start += duration_per_chapter
        chapter_num += 1

    clip.close()
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
        flash("Historial borrado ✅", "success")
        return redirect(url_for('history_page'))
    return render_template('history.html', videos=history)

@app.route('/link_download', methods=['GET', 'POST'])
def link_download():
    global history
    if request.method == 'POST':
        video_url = request.form['video_url']
        chapters = int(request.form['chapters'])
        duration = int(request.form['duration'])
        # Aquí se puede agregar descarga con yt_dlp si quieres
        # Por ahora se simula que se corta
        history.append(f"[LINK] Vídeo {video_url} cortado en {chapters} capítulos de {duration}s")
        flash(f"Vídeo de link procesado ✅", "success")
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
            filename = file.filename
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            # Cortar vídeo usando MoviePy
            try:
                output_files = cut_video(filepath, chapters, duration)
                history.append(f"[UPLOAD] {filename} cortado en {chapters} capítulos de {duration}s")
                flash(f"Archivo {filename} cortado correctamente ✅", "success")
            except Exception as e:
                flash(f"Error al cortar el vídeo: {e}", "danger")
            return redirect(url_for('history_page'))
    return render_template('upload_file.html')

@app.route('/downloads/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)