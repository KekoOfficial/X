from flask import Flask, render_template, request, jsonify, Response
import os, uuid, queue
from concurrent.futures import ThreadPoolExecutor
from config.database import db
from app.services.bot_service import run_mally_engine

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

executor = ThreadPoolExecutor(max_workers=20)
status_queue = queue.Queue()

# --- RUTAS DE NAVEGACIÓN ---
@app.route("/")
def home(): return render_template("upload.html")

@app.route("/settings")
def settings(): return render_template("settings.html")

@app.route("/history")
def history(): return render_template("history.html")

@app.route("/progress")
def progress(): return render_template("progress.html")

# --- API ---
@app.route("/api/status")
def stream():
    def event():
        while True:
            yield f"data: {status_queue.get()}\n\n"
    return Response(event(), mimetype="text/event-stream")

@app.route("/api/save_settings", methods=["POST"])
def save_db():
    db.save_config(request.json)
    return jsonify({"status": "success"})

@app.route("/api/upload_mally", methods=["POST"])
def handle_upload():
    file = request.files.get("video")
    temp_path = os.path.join("uploads", f"{uuid.uuid4().hex}.mp4")
    file.save(temp_path)
    
    # Inicia el proceso en segundo plano
    executor.submit(run_mally_engine, temp_path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
