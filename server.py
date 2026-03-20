from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import subprocess
import math

app = Flask(__name__)

UPLOAD_FOLDER = "/storage/emulated/0/Download/VideosServer"
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, "Cortados")
HISTORIAL_FILE = os.path.join(OUTPUT_FOLDER, "historial_cortes.txt")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    videos = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")]
    return render_template("index.html", videos=videos)

@app.route("/cut", methods=["POST"])
def cut_video():
    file = request.files["file"]
    cap_duration = int(request.form.get("cap_duration", 15))  # Duración por capítulo

    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)

    # Obtener duración total del vídeo
    result = subprocess.run(["ffprobe","-v","error","-show_entries",
                             "format=duration","-of",
                             "default=noprint_wrappers=1:nokey=1", filepath],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    total_duration = float(result.stdout)

    # Calcular número de capítulos automáticamente
    num_caps = math.ceil(total_duration / cap_duration)

    # Cortar vídeos
    start = 0
    cortados = []
    for i in range(num_caps):
        end = min(start + cap_duration, total_duration)
        outname = f"{os.path.splitext(filename)[0]}_cap{i+1}.mp4"
        outpath = os.path.join(OUTPUT_FOLDER, outname)
        subprocess.run(["ffmpeg", "-y", "-i", filepath, "-ss", str(start), "-to", str(end), "-c", "copy", outpath])
        cortados.append(outname)
        start = end

    # Guardar historial
    with open(HISTORIAL_FILE, "a") as f:
        for c in cortados:
            f.write(f"{filename} -> {c}\n")

    return jsonify({"success": True, "videos": cortados, "num_caps": num_caps})

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route("/clear_hist")
def clear_hist():
    open(HISTORIAL_FILE, "w").close()
    return jsonify({"success": True})

@app.route("/clear_folder")
def clear_folder():
    for f in os.listdir(OUTPUT_FOLDER):
        if f.endswith(".mp4"):
            os.remove(os.path.join(OUTPUT_FOLDER, f))
    open(HISTORIAL_FILE, "w").close()
    return jsonify({"success": True})

@app.route("/get_hist")
def get_hist():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r") as f:
            lines = f.readlines()
        return jsonify({"hist": lines})
    return jsonify({"hist": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)