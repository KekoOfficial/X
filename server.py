from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os, subprocess, math, datetime

# 🔥 Carpetas de trabajo
UPLOAD_FOLDER = "./uploads"
DOWNLOAD_FOLDER = "./downloads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# 📜 Historial de videos procesados
history = []

app = Flask(__name__)

# 🎯 Obtener duración del video en segundos
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

# 🚀 Reparar MP4 incompleto
def fix_mp4(path):
    fixed = path.replace(".mp4","_fixed.mp4")
    subprocess.run([
        "ffmpeg","-y","-i",path,
        "-c","copy","-movflags","faststart",
        fixed
    ])
    return fixed

# 🚀 Corte automático por capítulos
def cut_video(path, duration):
    total = get_duration(path)
    if total == 0:
        path = fix_mp4(path)
        total = get_duration(path)
        if total == 0:
            return "❌ No se puede procesar el video"

    parts = math.ceil(total / duration)
    name = os.path.splitext(os.path.basename(path))[0]

    for i in range(parts):
        start = i * duration
        output_name = f"{name}_capítulo_{i+1}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_name)

        cmd = [
            "ffmpeg","-y",
            "-ss", str(start),
            "-i", path,
            "-t", str(duration),
            "-c","copy",
            output_path
        ]
        subprocess.run(cmd)

    # Guardar en historial
    history.append({
        "name": name,
        "clips": parts,
        "date": str(datetime.datetime.now())
    })

# 🏠 HOME + Subida y corte automático
@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        if 'video_file' not in request.files:
            return "❌ No se envió ningún archivo", 400
        
        file = request.files['video_file']
        if file.filename == '':
            return "❌ No se seleccionó ningún archivo", 400

        try:
            duration = int(request.form['duration'])
        except:
            return "❌ Duración inválida", 400

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)
        cut_video(path, duration)
        return redirect(url_for('history_page'))

    return render_template("upload_file.html")

# 📜 Página de historial
@app.route('/history')
def history_page():
    return render_template("history.html", videos=history)

# 📥 Descargar clips
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

# 🚀 Inicio del servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)