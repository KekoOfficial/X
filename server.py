import os
import subprocess
from flask import Flask, request, render_template, send_from_directory, jsonify
import threading
import yt_dlp

app = Flask(__name__)

UPLOAD_FOLDER = "./VideosServer"
CORTADOS_FOLDER = os.path.join(UPLOAD_FOLDER, "Cortados")
HISTORIAL_FILE = os.path.join(CORTADOS_FOLDER, "historial_cortes.txt")
os.makedirs(CORTADOS_FOLDER, exist_ok=True)

# Función para cortar vídeo en capítulos
def cortar_video(path, dur_cap, videos_list):
    filename = os.path.basename(path)
    total_sec = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip())
    
    num_caps = int(total_sec // dur_cap) + (1 if total_sec % dur_cap > 0 else 0)
    
    cortados = []
    for i in range(num_caps):
        start = i * dur_cap
        end = min((i + 1) * dur_cap, total_sec)
        output_name = f"{os.path.splitext(filename)[0]}_cap{i+1}.mp4"
        output_path = os.path.join(CORTADOS_FOLDER, output_name)
        subprocess.run(["ffmpeg", "-y", "-i", path, "-ss", str(start), "-to", str(end),
                        "-c", "copy", output_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        cortados.append(output_name)
        with open(HISTORIAL_FILE, "a") as f:
            f.write(f"{filename} -> {output_name}\n")
        videos_list.append(output_name)
    return cortados

# Ruta principal
@app.route("/")
def index():
    cortados = [f for f in os.listdir(CORTADOS_FOLDER) if f.endswith(".mp4")]
    return render_template("index.html", videos=cortados)

# Subir y cortar vídeos locales
@app.route("/upload_cut", methods=["POST"])
def upload_cut():
    files = request.files.getlist("files")
    dur_cap = int(request.form.get("cap_duration", 15))
    videos_list = []
    def worker():
        for file in files:
            if file.filename.endswith(".mp4"):
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                cortar_video(filepath, dur_cap, videos_list)
    threading.Thread(target=worker).start()
    return jsonify({"status":"ok", "message":"Corte iniciado"}), 200

# Descargar desde URL (Dailymotion)
@app.route("/url_cut", methods=["POST"])
def url_cut():
    url = request.json.get("url")
    dur_cap = int(request.json.get("cap_duration", 15))
    videos_list = []
    def worker():
        ydl_opts = {'outtmpl': os.path.join(UPLOAD_FOLDER,'%(title)s.%(ext)s'),
                    'format':'bestvideo+bestaudio/best'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        cortar_video(filename, dur_cap, videos_list)
    threading.Thread(target=worker).start()
    return jsonify({"status":"ok", "message":"Descarga y corte iniciado"}), 200

# Descargar archivo cortado
@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(CORTADOS_FOLDER, filename, as_attachment=True)

# Limpiar carpeta cortados
@app.route("/clear_folder", methods=["POST"])
def clear_folder():
    for f in os.listdir(CORTADOS_FOLDER):
        if f.endswith(".mp4"):
            os.remove(os.path.join(CORTADOS_FOLDER, f))
    if os.path.exists(HISTORIAL_FILE):
        os.remove(HISTORIAL_FILE)
    return jsonify({"status":"ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)