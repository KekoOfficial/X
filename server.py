from flask import Flask, request, send_from_directory, jsonify
import os, subprocess, math

app = Flask(__name__)

# Carpetas de subida y salida
UPLOAD_FOLDER = "/storage/emulated/0/Download/VideosServer"
OUTPUT_FOLDER = "/storage/emulated/0/Download/CortadosKhasam"
HISTORIAL_FILE = os.path.join(OUTPUT_FOLDER, "historial_cortes.txt")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Progreso global
progress = {"total": 0, "done": 0, "status": ""}

def cortar_video(filepath, cap_duration):
    global progress
    # Obtener duración exacta
    result = subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration",
         "-of","default=noprint_wrappers=1:nokey=1", filepath],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    total_duration = float(result.stdout)
    num_caps = math.ceil(total_duration / cap_duration)

    start = 0
    cortados = []
    progress["total"] = num_caps
    progress["done"] = 0
    progress["status"] = "Cortando..."

    for i in range(num_caps):
        outname = f"{os.path.splitext(os.path.basename(filepath))[0]}_cap{i+1}.mp4"
        outpath = os.path.join(OUTPUT_FOLDER, outname)
        subprocess.run([
            "ffmpeg", "-y", "-i", filepath,
            "-ss", str(start), "-t", str(cap_duration),
            "-c", "copy", outpath
        ])
        cortados.append(outname)
        start += cap_duration
        progress["done"] += 1

    # Actualizar galería en Termux (si estás usando Android)
    subprocess.run(["termux-media-scan", OUTPUT_FOLDER])

    # Guardar historial
    with open(HISTORIAL_FILE, "a") as f:
        for c in cortados:
            f.write(f"{os.path.basename(filepath)} -> {c}\n")

    progress["status"] = "Listo"
    return cortados

@app.route("/upload", methods=["POST"])
def upload():
    files = request.files.getlist("files")
    cap_duration = int(request.form.get("cap_duration",15))
    all_cortados = []
    for f in files:
        if f.filename.endswith(".mp4"):
            filepath = os.path.join(UPLOAD_FOLDER, f.filename)
            f.save(filepath)
            cortados = cortar_video(filepath, cap_duration)
            all_cortados.extend(cortados)
    return jsonify({"cortados": all_cortados})

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

@app.route("/progress")
def get_progress():
    return jsonify(progress)

@app.route("/clear_history")
def clear_history():
    open(HISTORIAL_FILE,"w").close()
    return jsonify({"status":"ok"})

if __name__=="__main__":
    print("Servidor corriendo en http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000)