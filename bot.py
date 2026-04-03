import os, uuid, subprocess, requests, time, threading
from flask import Flask, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
log = Logger()
# Mantenemos el executor para que el servidor web siga libre mientras el bot trabaja
executor = ThreadPoolExecutor(max_workers=5)

def upload_worker(p_path, filename, part_num, total):
    """Sube la parte y retorna True si tuvo éxito para continuar la secuencia."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    try:
        with open(p_path, 'rb') as v:
            res = requests.post(url, data={
                'chat_id': CHAT_ID,
                'caption': f"📦 PARTE {part_num}/{total}\n🎬 {filename}\n⚡ MallyCuts Sincronizado",
                'supports_streaming': True
            }, files={'video': v}, timeout=300)
        
        if res.status_code == 200:
            log.success(f"✅ Parte {part_num} enviada con éxito.")
            os.remove(p_path)
            return True
        else:
            log.error(f"⚠️ Error en Telegram (Parte {part_num}): {res.status_code}")
            return False
    except Exception as e:
        log.error(f"❌ Error crítico subiendo parte {part_num}: {e}")
        return False

def synchronized_engine(input_path, filename):
    """Motor que corta en 60s y envía en orden estricto."""
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        # 1. SEGMENTACIÓN ULTRA-RÁPIDA (1 MINUTO)
        # Usamos -c copy para que el proceso sea casi instantáneo
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", "60", 
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        subprocess.run(cmd, capture_output=True, check=True)

        # 2. DETECTAR Y ORDENAR PARTES
        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)
        
        log.info(f"📦 Iniciando envío sincronizado de {total} partes...")
        
        # 3. ENVÍO SECUENCIAL (Para evitar el desorden)
        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            # El sistema espera a que cada parte se suba antes de ir a la siguiente
            # Esto garantiza el orden 1, 2, 3 en el chat de Telegram
            success = upload_worker(p_path, filename, i, total)
            
            # Pausa táctica de 1.5 segundos para asegurar la sincronía en la nube de Telegram
            if success:
                time.sleep(1.5)

        # Limpiar archivo original del servidor
        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"🔥 Proceso finalizado: {filename} enviado íntegramente.")

    except Exception as e:
        log.error(f"🔥 Fallo en el motor Sincronizado: {e}")

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/api/upload_pro", methods=["POST"])
def upload_pro():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400

    f_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, f"{f_id}_{file.filename}")
    file.save(path)

    # El motor arranca en un hilo separado para no bloquear la web
    executor.submit(synchronized_engine, path, file.filename)
    
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_folders()
    log.info("--- MALLY CUTS SYNC-PRO ONLINE ---")
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
