import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
log = Logger()
# Configurado para manejar múltiples subidas sin colapsar el buffer de Termux
executor = ThreadPoolExecutor(max_workers=10)

def mally_engine_v11(input_path, filename):
    """Motor MALLY v11: Reporte de inicio, segmentación flash y envío ordenado."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        # --- FICHA TÉCNICA DE INICIO ---
        inicio_msg = (
            "🚀 **MALLY CUTS v11: INICIANDO**\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"🎬 **Título:** {filename}\n"
            "⏱️ **Cortes:** 1 Minuto\n"
            "📦 **Estado:** Fragmentando...\n"
            "👑 **Creador:** Khassamx Dev\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': inicio_msg, 'parse_mode': 'Markdown'})

        log.info(f"⚡ MALLY V11: Procesando {filename}...")
        
        # MOTOR ULTRA-RÁPIDO (Stream Copy)
        # Corta sin renderizar, manteniendo calidad original al instante
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", "60", 
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # Obtener y ordenar las partes generadas
        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)

        # --- ENVÍO DE PARTES A TELEGRAM ---
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            with open(p_path, 'rb') as v:
                res = requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo", data={
                    'chat_id': CHAT_ID,
                    'caption': f"📦 **PARTE {i}/{total}**\n🎬 {filename}\n⚡ **MallyCuts v11**",
                    'parse_mode': 'Markdown',
                    'supports_streaming': True
                }, files={'video': v}, timeout=300)
            
            if res.status_code == 200:
                os.remove(p_path) # Limpieza inmediata para ahorrar espacio
                time.sleep(1.2) # Pausa de seguridad para orden cronológico
            else:
                log.error(f"⚠️ Error enviando parte {i}")

        # Limpieza del archivo original subido
        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"🔥 MALLY V11: Proceso completado ({total} partes).")

    except Exception as e:
        log.error(f"🔥 Fallo en Motor V11: {e}")
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={'chat_id': CHAT_ID, 'text': f"❌ **ERROR MALLY V11:**\n{str(e)}"})

# --- RUTAS DE ACCESO DIRECTO (SIN LOGIN) ---

@app.route("/")
def index():
    # Acceso directo al panel de control v11
    return render_template("upload.html")

@app.route("/api/upload_mally", methods=["POST"])
def upload_mally():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400

    # Generación de nombre único para evitar conflictos de archivos
    path = os.path.join(UPLOAD_FOLDER, f"V11_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    
    # Ejecución en segundo plano para no bloquear la web
    executor.submit(mally_engine_v11, path, file.filename)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    log.info("🛡️ MALLY CUTS V11 -
