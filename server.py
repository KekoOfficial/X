from flask import Flask, render_template, request, redirect, url_for, jsonify
import os, subprocess, math, threading, datetime

app = Flask(__name__)

UPLOAD = "uploads"
GALLERY = "/storage/emulated/0/Movies/MallyCuts"

os.makedirs(UPLOAD, exist_ok=True)
os.makedirs(GALLERY, exist_ok=True)

history = []
tasks = {}

# 🔥 Duración real del video
def get_duration(path):
    result = subprocess.run([
        "ffprobe","-v","error",
        "-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",
        path
    ], stdout=subprocess.PIPE)
    return float(result.stdout)

# 🚀 Corte automático
def process_video(task_id, path, duration):
    total = get_duration(path)
    parts = math.ceil(total / duration)

    name = os.path.splitext(os.path.basename(path))[0]
    folder = os.path.join(GALLERY, name)
    os.makedirs(folder, exist_ok=True)

    for i in range(parts):
        start = i * duration
        output = os.path.join(folder, f"{name} #{i+1}.mp4")

        cmd = [
            "ffmpeg","-y",
            "-ss", str(start),
            "-i", path,
            "-t", str(duration),
            "-c","copy",
            output
        ]

        print("Ejecutando:", " ".join(cmd))  # 🔥 DEBUG

        subprocess.run(cmd)  # SIN ocultar errores

        tasks[task_id]["progress"] = int(((i+1)/parts)*100)

    tasks[task_id]["status"] = "done"

    history.append({
        "name": name,
        "clips": parts,
        "date": str(datetime.datetime.now())
    })

    # 🧹 borrar archivo original
    try:
        os.remove(path)
    except:
        pass

# 🏠 HOME
@app.route('/')
def home():
    return render_template("index.html")

# 📁 PAGINA SUBIR
@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template("upload.html")

# 📁 SUBIR VIDEO
@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    duration = int(request.form['duration'])

    path = os.path.join(UPLOAD, file.filename)
    file.save(path)

    task_id = str(len(tasks)+1)

    tasks[task_id] = {
        "progress": 0,
        "status": "processing"
    }

    threading.Thread(target=process_video, args=(task_id, path, duration)).start()

    return redirect(url_for('home'))

# 📊 PROGRESO
@app.route('/progress/<task_id>')
def progress(task_id):
    return jsonify(tasks.get(task_id, {}))

# 📜 HISTORIAL
@app.route('/history')
def history_page():
    return render_template("history.html", history=history)

# 🧹 LIMPIAR
@app.route('/clear')
def clear():
    global history
    history = []
    return redirect(url_for('history_page'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)