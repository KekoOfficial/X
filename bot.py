import os
import uuid
import threading
import subprocess
import requests
import time
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, render_template, jsonify
from config import *
from logger import Logger

# Configuración del Motor
app = Flask(__name__)
log = Logger()
executor = ThreadPoolExecutor(max_workers=4) # Permite procesar varios videos a la vez

# Estados Globales en Memoria
JOBS = {}
TEMP_ANALYTICS = {}

# ==========================================
# 🛠️ NÚCLEO DE PROCESAMIENTO (AVANZADO)
# ==========================================

def get_detailed_info(file_path):
    """Análisis profundo del bitrate y streams del video."""
    try:
        cmd = [
            "ffprobe", "-v", "quiet", "-print_format", "json",
            "-show_format", "-show_streams", file_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        
        duration = float(data['format']['duration'])
        size_bytes = int(data['format']['size'])
        bitrate = int(data['format']['bit_rate'])
        
        return {
            "duration": duration,
            "size_mb": round(size_bytes / (1024 * 1024), 2),
            "bitrate_kbps": round(bitrate / 1000, 2),
            "format": data['format']['format_long_name']
        }
    except Exception as e:
        log.error(f"Error en ffprobe: {e}")
        return None

def smart_telegram_uploader(file_path, cap_num, job_id, retry=3):
    """Subida optimizada con reintentos automáticos y manejo de errores."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
    
    for attempt in range(retry):
        try:
            with open(file_path, 'rb') as v:
                payload = {
                    'chat_id': CHAT_ID,
                    'caption': f"📦 MallyCuts | Parte {cap_num}\n🆔 ID: {job_id}\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    'supports_streaming': True
                }
                res = requests.post(url, data=payload, files={'video': v}, timeout=300)
                
                if res.status_code == 200:
                    log.success(f"✅ [Job {job_id}] Parte {cap_num} enviada.")
                    return True
                else:
                    log.error(f"⚠️ Reintento {attempt+1}: Telegram respondió {res.status_code}")
        except Exception as e:
            log.error(f"❌ Error en intento {attempt+1}: {e}")
        time.sleep(5) # Espera antes de reintentar
    return False

def core_engine(job_id, input_path, filename, segment_time):
    """Motor FFmpeg con optimización de hilos y segmentación limpia."""
    start_time = time.time()
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")

    try:
        JOBS[job_id]["status"] = "processing"
        JOBS[job_id]["start_time"] = start_time

        # FFmpeg con copy de streams (0 pérdida de calidad y velocidad flash)
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0", 
            "-f", "segment", "-segment_time", str(segment_time),
            "-reset_timestamps", "1", "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        
        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode != 0:
            raise Exception(process.stderr)

        # Escaneo y envío
        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        JOBS[job_id]["total_parts"] = len(parts)

        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            success = smart_telegram_uploader(p_path, i, job_id)
            if success and os.path.exists(p_path):
                os.remove(p_path)
            JOBS[job_id]["current_part"] = i

        JOBS[job_id]["status"] = "completed"
        JOBS[job_id]["end_time"] = time.time()
        
        # Limpieza del original
        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"🚀 Job {job_id} terminado en {round(time.time()-start_time, 2)}s")

    except Exception as e:
        JOBS[job_id]["status"] = "failed"
        JOBS[job_id]["error"] = str(e)
        log.error(f"🔥 Fallo crítico en Motor: {e}")

# ==========================================
# 🌐 RUTAS WEB (CONTROL TOTAL)
# ==========================================

@app.route("/")
def dashboard():
    return render_template("upload.html")

@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Análisis previo para toma de decisiones."""
    file = request.files.get("video")
    if not file: return jsonify({"status": "error", "msg": "No file"}), 400

    f_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, f"{f_id}_{file.filename}")
    file.save(path)

    info = get_detailed_info(path)
    if not info: return jsonify({"status": "error", "msg": "Probe failed"}), 500

    # Generar predicción de capítulos
    prediction = {
        "3min": {"parts": int(info['duration'] // 180) + 1, "sec": 180},
        "5min": {"parts": int(info['duration'] // 300) + 1, "sec": 300},
        "10min": {"parts": int(info['duration'] // 600) + 1, "sec": 600}
    }

    TEMP_ANALYTICS[f_id] = {"path": path, "name": file.filename, "info": info}

    return jsonify({
        "file_id": f_id,
        "details": info,
        "predict": prediction
    })

@app.route("/api/execute", methods=["POST"])
def api_execute():
    """Lanzamiento del proceso tras confirmación del usuario."""
    data = request.json
    f_id = data.get("file_id")
    sec = int(data.get("seconds"))

    if f_id in TEMP_ANALYTICS:
        meta = TEMP_ANALYTICS[f_id]
        JOBS[f_id] = {"status": "queued", "name": meta['name']}
        
        # Ejecución asíncrona
        executor.submit(core_engine, f_id, meta['path'], meta['name'], sec)
        return jsonify({"status": "success", "job_id": f_id})
    
    return jsonify({"status": "error", "msg": "Session expired"}), 404

@app.route("/api/status/<job_id>")
def api_status(job_id):
    """Endpoint de monitoreo en tiempo real."""
    return jsonify(JOBS.get(job_id, {"status": "not_found"}))

if __name__ == "__main__":
    init_folders()
    log.info("--- MALLY CUTS ADVANCED ENGINE ONLINE ---")
    app.run(host=HOST, port=PORT, debug=DEBUG, threaded=True)
