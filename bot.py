# bot.py - MALLY CUTS v12 (Khassamx Dev Edition)
import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
log = Logger()
# 10 hilos para gestionar la subida masiva a Telegram sin bloqueos
executor = ThreadPoolExecutor(max_workers=10)

def mally_engine_v12(input_path, filename):
    """Motor v12: Reporte de inicio y segmentación ultra-rápida."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        # --- REPORTE DE LANZAMIENTO IMPERIAL ---
        inicio_msg = (
            "📢 **MALLY SERIES: NUEVO ESTRENO**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 **Título:** {filename}\n"
            "⏱️ **Cortes:** Partes de 1 min\n"
            "📦 **Estado:** Procesando...\n"
            "👑 **Creador:** Khassamx Dev\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': inicio_msg, 'parse_mode': 'Markdown'})

        log.info(f"⚡ MALLY V12: Iniciando corte de {filename}...")
        
        # FFmpeg v12: Velocidad luz mediante copiado de flujo
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", "60", 
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # Ordenar partes alfabéticamente para mantener la secuencia
        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)

        # --- ENVÍO SECUENCIAL AL CANAL ---
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            with open(p_path, 'rb') as v:
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                    'chat_id': CHAT_ID,
                    'caption': f"📦 **{filename} - PARTE {i}/{total}**\n\n📺 @MallySeries\n⚡ **MallyCuts v12**",
                    'parse_mode': 'Markdown',
                    'supports_streaming': True
                }, files={'video': v}, timeout=300)
            
            os.remove(p_path) # Limpieza para optimizar memoria en Termux
            time.sleep(1.2) # Pausa para asegurar el orden cronológico en el canal

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"🔥 MALLY V12: {total} partes enviadas a Mally Series.")

    except Exception as e:
        log.error(f"🔥 Fallo en Motor v12: {e}")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': f"❌ **ERROR SISTEMA V12:**\n{str(e)}"})

# --- RUTAS DE ACCESO DIRECTO ---

@app.route("/")
def index():
    # Carga directa del panel MALLY CUTS sin login
    return render_template("upload.html")

@app.route("/api/upload_mally", methods=["POST"])
def upload_mally():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400

    # Nombre de archivo único v12
    path = os.path.join(UPLOAD_FOLDER, f"V12_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    
    executor.submit(mally_engine_v12, path, file.filename)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    log.info("🛡️ MALLY CUTS V12 - KHASSAMX DEV ONLINE")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
