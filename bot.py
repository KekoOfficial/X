import os, uuid, subprocess, requests, time
from flask import Flask, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import *
from logger import Logger

app = Flask(__name__)
log = Logger()
# Aumentamos los hilos para procesar la subida mientras se corta el siguiente
executor = ThreadPoolExecutor(max_workers=8) 

def fast_segmenter(job_id, input_path, filename):
    """Corta videos de 1 hora en partes de 5 min casi instantáneamente."""
    base = os.path.splitext(filename)[0]
    # Usamos un patrón de salida que FFmpeg reconoce para numerar partes
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")
    
    try:
        # COMANDO PRO: Copy de streams + FastStart + Segmentación de 300s
        # Esto no recodifica, por lo que es la velocidad máxima física del disco.
        cmd = [
            "ffmpeg", "-y", "-i", input_path,
            "-c", "copy", "-map", "0",
            "-f", "segment", "-segment_time", "300",
            "-reset_timestamps", "1",
            "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)
        
        # Obtener lista de partes generadas
        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)

        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            # Subida directa a Telegram
            with open(p_path, 'rb') as v:
                requests.post(
                    f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                    data={
                        'chat_id': CHAT_ID,
                        'caption': f"🎬 {filename}\n📦 Parte {i}/{total}\n⚡ MallyCuts Pro",
                        'supports_streaming': True
                    },
                    files={'video': v}, timeout=300
                )
            os.remove(p_path) # Limpieza inmediata para ahorrar espacio en Termux

        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"✅ Sistema Pro: {filename} enviado en {total} partes.")

    except Exception as e:
        log.error(f"❌ Error en Motor Pro: {e}")

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

    # Disparar el motor inmediatamente sin preguntar nada
    executor.submit(fast_segmenter, f_id, path, file.filename)
    
    return jsonify({"status": "success", "job_id": f_id})

if __name__ == "__main__":
    init_folders()
    app.run(host=HOST, port=PORT, debug=False, threaded=True)
