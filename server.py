from flask import Flask, request, render_template, send_from_directory, jsonify
import os
import subprocess
import math
import threading

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = os.path.join(UPLOAD_FOLDER, "Cortados")
HISTORIAL_FILE = os.path.join(OUTPUT_FOLDER, "historial_cortes.txt")
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Variable para progreso global
progress = {"total":0, "done":0, "status":""}

def cortar_video(filepath, cap_duration):
    global progress
    result = subprocess.run(
        ["ffprobe","-v","error","-show_entries",
         "format=duration","-of","default=noprint_wrappers=1:nokey=1", filepath],
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
        end = min(start + cap_duration, total_duration)
        outname = f"{os.path.splitext(os.path.basename(filepath))[0]}_cap{i+1}.mp4"
        outpath = os.path.join(OUTPUT_FOLDER, outname)
        subprocess.run(["ffmpeg", "-y", "-i", filepath, "-ss", str(start), "-to", str(end), "-c", "copy", outpath])
        cortados.append(outname)
        start = end
        progress["done"] += 1

    # Guardar historial
    with open(HISTORIAL_FILE, "a") as f:
        for c in cortados:
            f.write(f"{os.path.basename(filepath)} -> {c}\n")

    progress["status"] = "Listo"
    return cortados

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/cut", methods=["POST"])
def cut():
    file = request.files["file"]
    cap_duration = int(request.form.get("cap_duration", 15))
    filename = file.filename
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    file.save(filepath)

    thread = threading.Thread(target=cortar_video, args=(filepath, cap_duration))
    thread.start()
    return jsonify({"success": True, "message":"Corte iniciado..."})

@app.route("/progress")
def get_progress():
    if progress["total"] == 0:
        perc = 0
    else:
        perc = int(progress["done"]/progress["total"]*100)
    return jsonify({"done": progress["done"], "total": progress["total"], "percent": perc, "status": progress["status"]})

@app.route("/get_hist")
def get_hist():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, "r") as f:
            lines = f.readlines()
        return jsonify({"hist": lines})
    return jsonify({"hist":[]})

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

@app.route("/download/<filename>")
def download(filename):
    return send_from_directory(OUTPUT_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)