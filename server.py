from flask import Flask, request, render_template, send_from_directory
import os
import subprocess
import json

app = Flask(__name__)

UPLOAD_FOLDER = "/storage/emulated/0/Download/VideosServer"
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, "Cortados")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Obtener duración
def get_duration(file):
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", file
    ], capture_output=True, text=True)

    data = json.loads(result.stdout)
    return float(data["format"]["duration"])


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = request.files.getlist("files")
        segment_time = int(request.form.get("duration", 15))  # 🔥 duración elegida

        count = len([f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")])

        for file in files:
            try:
                filename = file.filename
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                file.save(filepath)

                duration = get_duration(filepath)

                # 🔥 calcular cuántos clips
                total_parts = int(duration // segment_time)

                print(f"Duración: {duration}s | Segmento: {segment_time}s | Clips: {total_parts}")

                for i in range(total_parts):
                    start = i * segment_time

                    count += 1
                    output_name = f"video_{count}_part{i+1}.mp4"
                    output_path = os.path.join(OUTPUT_FOLDER, output_name)

                    subprocess.run([
                        "ffmpeg",
                        "-ss", str(start),
                        "-i", filepath,
                        "-t", str(segment_time),
                        "-c", "copy",
                        output_path
                    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            except Exception as e:
                print("Error:", e)
                continue

    videos = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")]
    return render_template("index.html", videos=videos)


@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    print("🔥 Khasam Cutter PRO activo en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)