from flask import Flask, request, render_template, send_from_directory
import os
import subprocess
import json
from datetime import datetime

app = Flask(__name__)

UPLOAD_FOLDER = "/storage/emulated/0/Download/VideosServer"
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, "Cortados")
HISTORIAL_FILE = os.path.join(OUTPUT_FOLDER, "historial.json")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Crear historial si no existe
if not os.path.exists(HISTORIAL_FILE):
    with open(HISTORIAL_FILE, "w") as f:
        json.dump([], f)

# Obtener duración del video
def get_duration(file):
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", file
    ], capture_output=True, text=True)

    data = json.loads(result.stdout)
    return float(data["format"]["duration"])

# Guardar historial
def guardar_historial(nombre, duracion, partes):
    with open(HISTORIAL_FILE, "r") as f:
        data = json.load(f)

    data.append({
        "video": nombre,
        "duracion": duracion,
        "clips": partes,
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

    with open(HISTORIAL_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("files")
        segment_time = int(request.form.get("duration", 15))

        count = len([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")])

        for file in files:
            try:
                filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                duration = get_duration(filepath)
                total_parts = int(duration // segment_time)

                for i in range(total_parts):
                    start = i * segment_time

                    count += 1
                    output_name = f"video_{count}_part{i+1}.mp4"
                    output_path = os.path.join(OUTPUT_FOLDER, output_name)

                    # 🔥 CORTE EXACTO
                    subprocess.run([
                        "ffmpeg",
                        "-i", filepath,
                        "-ss", str(start),
                        "-t", str(segment_time),
                        "-c:v", "libx264",
                        "-c:a", "aac",
                        "-preset", "ultrafast",
                        "-crf", "23",
                        output_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                guardar_historial(filename, round(duration,2), total_parts)

            except Exception as e:
                print("Error:", e)
                continue

    videos = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")]

    with open(HISTORIAL_FILE, "r") as f:
        historial = json.load(f)

    historial = list(reversed(historial))  # último primero

    return render_template("index.html", videos=videos, historial=historial)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    print("🔥 Khasam Cutter PRO activo en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)