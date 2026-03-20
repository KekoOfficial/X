from flask import Flask, request, render_template_string, send_from_directory, jsonify
import os, subprocess, math

app = Flask(__name__)

# Carpeta de subida y salida
UPLOAD_FOLDER = "/storage/emulated/0/Download/VideosServer"
OUTPUT_FOLDER = "/storage/emulated/0/Download/CortadosKhasam"
HISTORIAL_FILE = os.path.join(OUTPUT_FOLDER, "historial_cortes.txt")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Variable global de progreso
progress = {"total": 0, "done": 0, "status": ""}

# HTML + CSS + JS
HTML_PAGE = """
<!doctype html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Cortador de Vídeos Khasam</title>
<style>
body { font-family: Arial; background:#1c1c1c; color:#f0f0f0; display:flex; flex-direction:column; align-items:center; padding:30px;}
h1 { color:#00ffff; margin-bottom:20px; }
form { background:#333; padding:20px; border-radius:10px; margin-bottom:20px; width:350px; }
input, button, select { margin:5px 0; padding:10px; border-radius:5px; border:none; width:100%; font-size:16px; }
button { background:#00ffff; color:#000; cursor:pointer; }
ul { list-style:none; padding:0; width:350px; }
a { color:#00ffff; text-decoration:none; word-wrap: break-word; }
.progress-container { width: 100%; background: #555; border-radius: 5px; margin:10px 0; height:20px; }
.progress-bar { height:100%; width:0%; background:#00ffff; border-radius:5px;}
h3 { margin:10px 0; color:#ff0; }
.clear-btn { background:#ff0000; color:#fff; }
</style>
</head>
<body>
<h1>🎬 Cortador de Vídeos Khasam</h1>
<form id="cutForm" method="post" enctype="multipart/form-data">
<label>Selecciona vídeos (MP4):</label>
<input type="file" name="files" multiple required>
<label>Duración de capítulo (segundos):</label>
<select name="cap_duration" required>
  <option value="15">15</option>
  <option value="30">30</option>
  <option value="60">60</option>
</select>
<button type="submit">Cortar Vídeos</button>
</form>

<div class="progress-container">
  <div class="progress-bar" id="progressBar"></div>
</div>
<h3 id="progressStatus"></h3>

<button class="clear-btn" onclick="clearHistory()">Borrar historial</button>

<h2>Vídeos cortados:</h2>
<ul id="videosList">
{% for video in videos %}
<li><a href="/download/{{ video }}">{{ video }}</a></li>
{% endfor %}
</ul>

<script>
const form = document.getElementById("cutForm");
const progressBar = document.getElementById("progressBar");
const progressStatus = document.getElementById("progressStatus");
const videosList = document.getElementById("videosList");

form.onsubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const response = await fetch("/", {method:"POST", body: formData});
    const data = await response.json();
    monitorProgress();
};

async function monitorProgress(){
    let interval = setInterval(async ()=>{
        const resp = await fetch("/progress");
        const prog = await resp.json();
        if(prog.total>0){
            let perc = Math.round((prog.done/prog.total)*100);
            progressBar.style.width = perc+"%";
            progressStatus.innerText = prog.status + " ("+prog.done+"/"+prog.total+")";
        }
        if(prog.status=="Listo"){
            clearInterval(interval);
            location.reload();
        }
    },500);
}

async function clearHistory(){
    await fetch("/clear_history");
    alert("Historial borrado!");
    location.reload();
}
</script>
</body>
</html>
"""

def cortar_video(filepath, cap_duration):
    global progress
    # Obtener duración del vídeo
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

    # Escanear carpeta para galería
    subprocess.run(["termux-media-scan", OUTPUT_FOLDER])

    # Guardar historial
    with open(HISTORIAL_FILE, "a") as f:
        for c in cortados:
            f.write(f"{os.path.basename(filepath)} -> {c}\n")

    progress["status"] = "Listo"
    return cortados

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method=="POST":
        files = request.files.getlist("files")
        cap_duration = int(request.form.get("cap_duration",15))
        all_cortados = []
        for f in files:
            if f.filename.endswith(".mp4"):
                filepath = os.path.join(UPLOAD_FOLDER, f.filename)
                f.save(filepath)
                cortados = cortar_video(filepath, cap_duration)
                all_cortados.extend(cortados)
        return jsonify({"status":"ok", "files":all_cortados})

    videos = [f for f in os.listdir(OUTPUT_FOLDER) if f.endswith(".mp4")]
    return render_template_string(HTML_PAGE, videos=videos)

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