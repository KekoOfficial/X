import os, uuid, threading, subprocess, requests, time, json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
from flask_sqlalchemy import SQLAlchemy
from config import *
from logger import Logger

# Configuración de Élite
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mally_empire.db'
app.config['SECRET_KEY'] = 'mally_secret_key'

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
log = Logger()
executor = ThreadPoolExecutor(max_workers=4)

# ==========================================
# 📊 BASE DE DATOS (HISTORIAL IMPERIAL)
# ==========================================
class VideoJob(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    filename = db.Column(db.String(100))
    status = db.Column(db.String(20), default="queued")
    parts_total = db.Column(db.Integer, default=0)
    parts_done = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context():
    db.create_all()

# ==========================================
# ⚙️ MOTOR DE PROCESAMIENTO ASÍNCRONO
# ==========================================

def update_status(job_id, status, current=None, total=None):
    """Notifica a la web en tiempo real vía WebSockets."""
    with app.app_context():
        job = VideoJob.query.get(job_id)
        if job:
            job.status = status
            if current is not None: job.parts_done = current
            if total is not None: job.parts_total = total
            db.session.commit()
    
    socketio.emit('status_update', {
        'job_id': job_id,
        'status': status,
        'current': current,
        'total': total
    })

def core_engine(job_id, input_path, filename, segment_time):
    start_time = time.time()
    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")

    try:
        update_status(job_id, "processing")
        
        # FFmpeg Ultra-Fast Segmenter
        cmd = [
            "ffmpeg", "-y", "-i", input_path, "-c", "copy", "-map", "0", 
            "-f", "segment", "-segment_time", str(segment_time),
            "-reset_timestamps", "1", "-segment_format_options", "movflags=+faststart",
            output_pattern
        ]
        
        subprocess.run(cmd, capture_output=True, check=True)

        parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
        total = len(parts)
        update_status(job_id, "uploading", 0, total)

        for i, p_name in enumerate(parts, 1):
            p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
            
            # Subida con Reintento Inteligente
            success = False
            for _ in range(3):
                with open(p_path, 'rb') as v:
                    res = requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo",
                        data={'chat_id': CHAT_ID, 'caption': f"📦 Parte {i}/{total}\n🆔 {job_id}", 'supports_streaming': True},
                        files={'video': v}, timeout=300
                    )
                    if res.status_code == 200:
                        success = True; break
                time.sleep(5)

            if success:
                os.remove(p_path)
                update_status(job_id, "uploading", i, total)

        update_status(job_id, "completed", total, total)
        if os.path.exists(input_path): os.remove(input_path)
        log.success(f"✅ Job {job_id} exitoso.")

    except Exception as e:
        update_status(job_id, "failed")
        log.error(f"Fallo crítico: {e}")

# ==========================================
# 🌐 RUTAS DE CONTROL
# ==========================================

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/history")
def history():
    jobs = VideoJob.query.order_by(VideoJob.timestamp.desc()).limit(10).all()
    return render_template("history.html", jobs=jobs)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400

    f_id = str(uuid.uuid4())[:8]
    path = os.path.join(UPLOAD_FOLDER, f"{f_id}_{file.filename}")
    file.save(path)

    # Info Técnica
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(res.stdout)
    dur = float(info['format']['duration'])

    new_job = VideoJob(id=f_id, filename=file.filename)
    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        "file_id": f_id,
        "duration": round(dur, 2),
        "options": {
            "Corte 3m": {"sec": 180, "parts": int(dur // 180) + 1},
            "Corte 5m": {"sec": 300, "parts": int(dur // 300) + 1}
        }
    })

@app.route("/api/execute", methods=["POST"])
def execute():
    data = request.json
    f_id = data.get("file_id")
    sec = int(data.get("seconds"))
    
    job = VideoJob.query.get(f_id)
    if job:
        path = [f for f in os.listdir(UPLOAD_FOLDER) if f.startswith(f_id)][0]
        executor.submit(core_engine, f_id, os.path.join(UPLOAD_FOLDER, path), job.filename, sec)
        return jsonify({"status": "success", "job_id": f_id})
    return jsonify({"status": "error"}), 404

if __name__ == "__main__":
    init_folders()
    log.info("🔥 MALLY CUTS v3.0 INICIADO")
    socketio.run(app, host=HOST, port=PORT, debug=DEBUG)
