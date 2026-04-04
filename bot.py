import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify, session
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
app.secret_key = "MALLY_CUTS_ULTIMATE"
log = Logger()
# Máxima potencia para subidas paralelas controladas
executor = ThreadPoolExecutor(max_workers=10)

# SEGURIDAD MALLY
ADMIN_PASS = "1234" 

def mally_engine(input_path, filename):
    """Motor MALLY: Corte instantáneo y envío sincronizado a Telegram."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        log.info(f"⚡ MALLY CUTS: Iniciando segmentación flash de {filename}")
        
        # CORTE INSTANTÁNEO (Sin renderizado para máxima velocidad)
        # Corta en fragmentos exactos de 1 minuto
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", "60", 
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        
        # Procesa una hora de video en menos de 20 segundos
        subprocess.run(cmd, capture_output=True, check=True)

        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)
        log.info(f"📦 MALLY: {total} partes listas para Telegram.")

        # ENVÍO ORDENADO Y RÁPIDO
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            with open(p_path, 'rb') as v:
                # Se eliminó el modo silencio para confirmar recepción con sonido
                res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                    'chat_id': CHAT_ID,
                    'caption': f"📦 MALLY PART {i}/{total}\n🎬 {filename}\n⚡ MallyCuts Sincronizado",
                    'supports_streaming': True
                }, files={'video': v}, timeout=300)
            
            if res.status_code == 200:
                os.remove(p_path)
                # Pausa mínima de 1.1s para mantener el orden estricto en el chat
                time.sleep(1.1)
            else:
                log.error(f"⚠️ Error en parte {i}")

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"🔥 MALLY CUTS: Envío de {total} partes finalizado.")

    except Exception as e:
        log.error(f"🔥 Error en motor MALLY: {e}")

# --- RUTAS ---

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

@app.route("/api/upload_mally", methods=["POST"])
def upload_mally():
    if "auth" not in session: return jsonify({"status": "forbidden"}), 403
    
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400

    path = os.path.join(UPLOAD_FOLDER, f"MALLY_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    
    # Inicia el motor optimizado
    executor.submit(mally_engine, path, file.filename)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
