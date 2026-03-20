from flask import Flask, render_template, request, send_from_directory, jsonify
import os
import subprocess
import yt_dlp

app = Flask(__name__)

DOWNLOAD_FOLDER = os.path.join(os.getcwd(), "Downloads")
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
HISTORIAL_FILE = os.path.join(DOWNLOAD_FOLDER, "historial.txt")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)

@app.route("/cut", methods=["POST"])
def cut_video():
    url = request.form.get("url")
    duration = int(request.form.get("duration"))  # duración por capítulo en segundos
    chapters = int(request.form.get("chapters"))

    # Descargar el vídeo usando yt-dlp
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, 'video.%(ext)s')
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    input_video = os.path.join(DOWNLOAD_FOLDER, "video.mp4")
    # Obtener duración total con ffprobe
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_video],
        capture_output=True, text=True
    )
    total_seconds = float(result.stdout.strip())
    chapter_duration = total_seconds / chapters

    # Cortar vídeos en capítulos
    output_files = []
    for i in range(chapters):
        start = i * chapter_duration
        end = min((i + 1) * chapter_duration, total_seconds)
        output_name = f"video_{i+1}.mp4"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_name)
        subprocess.run([
            "ffmpeg", "-i", input_video, "-ss", str(start), "-to", str(end),
            "-c", "copy", output_path, "-y"
        ])
        output_files.append(output_name)

        # Guardar en historial
        with open(HISTORIAL_FILE, "a") as f:
            f.write(f"{output_name} ({start:.2f}-{end:.2f}s)\n")

    return jsonify({"status": "ok", "files": output_files})

@app.route("/historial")
def historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r") as f:
            lines = f.readlines()
        return jsonify({"historial": [line.strip() for line in lines]})
    return jsonify({"historial": []})

@app.route("/clear_historial")
def clear_historial():
    if os.path.exists(HISTORIAL_FILE):
        os.remove(HISTORIAL_FILE)
    return jsonify({"status": "ok"})

@app.route("/clear_folder")
def clear_folder():
    for f in os.listdir(DOWNLOAD_FOLDER):
        if f.endswith(".mp4"):
            os.remove(os.path.join(DOWNLOAD_FOLDER, f))
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)