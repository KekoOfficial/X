import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify, session
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
app.secret_key = "IMP_V10_FLASH"
log = Logger()
# Aumentamos a 10 trabajadores para gestionar mejor las subidas paralelas
executor = ThreadPoolExecutor(max_workers=10)

ADMIN_PASS = "1234" 

def flash_engine(input_path, filename):
    """Motor optimizado: Solo velocidad y orden estricto."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        log.info(f"⚡ Iniciando Corte Flash: {filename}")
        
        # SEGMENTACIÓN INSTANTÁNEA (Usa 'copy' para no tardar nada)
        # Corta en fragmentos de 60 segundos (1 minuto)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", "60", 
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        
        # El corte de un video de 1 hora debería tardar menos de 20 segundos
        subprocess.run(cmd, capture_output=True, check=True)

        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)
        log.info(f"📦 {total} partes listas. Iniciando envío sincronizado...")

        # ENVÍO SECUENCIAL (Para garantizar el orden 1, 2, 3...)
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            with open(p_path, 'rb') as v:
                # Se eliminó 'disable_notification' para que siempre avise
                res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                    'chat_id': CHAT_ID,
                    'caption': f"📦 PARTE {i}/{total}\n🎬 {filename}\n⚡ MallyCuts Sincronizado",
                    'supports_streaming': True
                }, files={'video': v}, timeout=300)
            
            if res.status_code == 200:
                os.remove(p_path) # Borrar para no llenar Termux
                # Pausa mínima de 1.2s para asegurar que Telegram no los desordene
                time.sleep(1.2)
            else:
                log.error(f"⚠️ Error enviando parte {i}")

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"🔥 Proceso finalizado: {total} partes enviadas en orden.")

    except Exception as e:
        log.error(f"🔥 Fallo en el motor: {e}")

# --- RUTAS SIMPLIFICADAS ---

@app.route("/")
def index():
    if "auth" in session:
        return render_template("upload.html")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    if request.form.get("password") == ADMIN_PASS:
        session["auth"] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "error"}), 401

@app.route("/api/upload_v10", methods=["POST"])
def upload_v10():
    if "auth" not in session: return jsonify({"status": "forbidden"}), 403
    
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400

    path = os.path.join(UPLOAD_FOLDER, f"V10_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    
    # Dispara el motor sin opciones raras, directo al grano
    executor.submit(flash_engine, path, file.filename)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
