import os
import uuid
import threading
import subprocess
import requests
from flask import Flask, request, render_template, jsonify
from config import BOT_TOKEN, CHAT_ID, HOST, PORT, DEBUG, UPLOAD_FOLDER, DOWNLOAD_FOLDER, init_folders

app = Flask(__name__)

# Inicializar carpetas al arrancar
init_folders()

# Diccionario para rastrear el progreso de los videos
JOBS = {}

def enviar_a_telegram(file_path, cap_num, job_id):
    """Envía el clip a Telegram y lo elimina del servidor inmediatamente."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        with open(file_path, 'rb') as video_file:
            payload = {
                'chat_id': CHAT_ID, 
                'caption': f"🎬 MallyCuts | Capítulo {cap_num}\n🆔 Job: {job_id}"
            }
            files = {'video': video_file}
            response = requests.post(url, data=payload, files=files)
            
            if response.status_code == 200:
                print(f"✅ Capítulo {cap_num} enviado con éxito.")
                os.remove(file_path) # Limpieza inmediata
            else:
                print(f"❌ Error al enviar a Telegram: {response.text}")
    except Exception as e:
        print(f"⚠️ Excepción en el envío: {e}")

def process_video(job_id, input_path, filename, segment_time):
    """Procesa el video con FFmpeg y gestiona el envío secuencial."""
    base_name = os.path.splitext(filename)[0]
    # Patrón de salida para los capítulos
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base_name}_cap_%03d.mp4")

    try:
        # Comando FFmpeg: Corte por tiempo sin re-codificar (rápido)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-f", "segment",
            "-segment_time", str(segment_time),
            "-reset_timestamps", "1", 
            output_pattern
        ]
        
        subprocess.run(cmd, check=True)

        # Buscar todos los capítulos generados
        capitulos = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base_name)])
        
        for i, cap_name in enumerate(capitulos, 1):
            cap_path = os.path.join(DOWNLOAD_FOLDER, cap_name)
            enviar_a_telegram(cap_path, i, job_id)

        JOBS[job_id]["status"] = "done"
        # Eliminar el video original para ahorrar espacio
        if os.path.exists(input_path):
            os.remove(input_path)

    except Exception as e:
        JOBS[job_id]["status"] = "error"
        JOBS[job_id]["error"] = str(e)
        print(f"❌ Error en el proceso {job_id}: {e}")

@app.route("/", methods=["GET"])
def index():
    return render_template("upload_file.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("video")
    # Capturar la opción de tiempo del formulario (300s = 5min por defecto)
    time_choice = int(request.form.get("time_choice", 300))

    if not file or file.filename == "":
        return "No seleccionaste ningún archivo", 400

    job_id = str(uuid.uuid4())[:8]
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(input_path)

    JOBS[job_id] = {"status": "processing", "progress": 0}

    # Iniciar procesamiento en segundo plano
    thread = threading.Thread(
        target=process_video, 
        args=(job_id, input_path, file.filename, time_choice)
    )
    thread.start()

    return render_template("processing.html", job_id=job_id)

@app.route("/progress/<job_id>")
def progress(job_id):
    return jsonify(JOBS.get(job_id, {"status": "not_found"}))

if __name__ == "__main__":
    # Asegúrate de que las carpetas existan antes de correr el server
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
