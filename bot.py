import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify, session
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
app.secret_key = "IMP_V10_ULTIMATE" # Llave maestra de sesión
log = Logger()
executor = ThreadPoolExecutor(max_workers=5)

# CONFIGURACIÓN DE SEGURIDAD V10
ADMIN_PASS = "1234" # Tu clave de acceso

# --- MOTORES DE PROCESAMIENTO ---

def process_engine(input_path, filename, segment_time, is_tiktok):
    """Motor v10: Telegram Standard o TikTok Vertical."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        if is_tiktok:
            log.info(f"🎵 Modo TikTok Activo: Reencuadrando a 9:16...")
            # Filtro profesional: Escala, Recorte y Optimización móvil
            vf_chain = "scale=ih*9/16:ih,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1"
            codec = ["-c:v", "libx264", "-preset", "ultrafast", "-crf", "23"]
        else:
            log.info(f"✈️ Modo Telegram Activo: Corte Sincronizado...")
            vf_chain = "copy"
            codec = ["-c", "copy"] # Ultra rápido sin re-encodear

        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-vf", vf_chain if is_tiktok else "null",
            *codec, "-map", "0",
            "-f", "segment", "-segment_time", str(segment_time),
            "-reset_timestamps", "1",
            output_pattern
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)

        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)

        # Envío Sincronizado v10
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            mode_label = "📱 TIKTOK DRAFT" if is_tiktok else "✈️ TELEGRAM PART"
            
            with open(p_path, 'rb') as v:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                    'chat_id': CHAT_ID,
                    'caption': f"{mode_label}\n📦 PARTE {i}/{total}\n🎬 {filename}\n#MallyCutsV10 #ImperioIMP",
                    'supports_streaming': True
                }, files={'video': v})
            
            os.remove(p_path) # Limpieza en tiempo real
            time.sleep(1.3)

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"✅ Secuencia v10 completada para {filename}")

    except Exception as e:
        log.error(f"🔥 Error Crítico Motor v10: {e}")

# --- RUTAS E INTERFAZ ---

@app.route("/")
def index():
    if "auth" in session:
        return render_template("upload.html") # Panel de Control
    return render_template("login.html") # Pantalla de Bloqueo

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
    sec = int(request.form.get("seconds", 60))
    is_tiktok = request.form.get("tiktok") == "true" # Nuevo parámetro v10

    if not file: return jsonify({"status": "error"}), 400

    path = os.path.join(UPLOAD_FOLDER, f"V10_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    
    executor.submit(process_engine, path, file.filename, sec, is_tiktok)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    log.info("🛡️ MALLYCUTS V10 PROTECTED ONLINE")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
