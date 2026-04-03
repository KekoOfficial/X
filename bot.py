import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
app.secret_key = "IMP_SECRET_KEY_2026" # Llave para las sesiones
log = Logger()
executor = ThreadPoolExecutor(max_workers=5)

# CONFIGURACIÓN DE ACCESO IMPERIAL
ADMIN_PASS = "1234" # Cambia esta clave por la que quieras

def synchronized_engine(input_path, filename, segment_time, silent_mode):
    """Motor optimizado para TikTok con Formato Vertical."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        log.info(f"🎨 Renderizando clips para TikTok: {filename}")
        # Comando FFmpeg: Ajusta a 9:16 y optimiza para móvil
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", "scale=ih*9/16:ih,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-f", "segment", "-segment_time", str(segment_time),
            "-reset_timestamps", "1",
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)

        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            with open(p_path, 'rb') as v:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                    'chat_id': CHAT_ID,
                    'caption': f"📱 TIKTOK DRAFT\n📦 PARTE {i}/{total}\n🎬 {filename}\n#ImperioIMP #MallyCuts",
                    'supports_streaming': True,
                    'disable_notification': silent_mode
                }, files={'video': v}, timeout=300)
            os.remove(p_path)
            time.sleep(1.5)

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"✅ Clips listos para TikTok enviando a Telegram.")
    except Exception as e:
        log.error(f"🔥 Error en Motor TikTok: {e}")

# --- RUTAS DE SESIÓN ---

@app.route("/")
def index():
    if "logged_in" in session:
        return render_template("upload.html")
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    password = request.form.get("password")
    if password == ADMIN_PASS:
        session["logged_in"] = True
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "Clave Incorrecta"}), 401

@app.route("/api/upload_pro", methods=["POST"])
def upload_pro():
    if "logged_in" not in session: return jsonify({"status": "forbidden"}), 403
    
    file = request.files.get("video")
    sec = int(request.form.get("seconds", 60))
    silent = request.form.get("silent") == "true"

    if not file: return jsonify({"status": "error"}), 400

    f_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, f"{f_id}_{file.filename}")
    file.save(path)
    executor.submit(synchronized_engine, path, file.filename, sec, silent)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
