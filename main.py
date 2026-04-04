import os, uuid, json, queue
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from config import init_nexus, DB_PATH
from bot import start_mally_engine
from logger import Logger

app = Flask(__name__)
log = Logger()
# 20 hilos para que la web siempre responda instantáneamente
executor = ThreadPoolExecutor(max_workers=20)
status_queue = queue.Queue()

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/settings")
def settings_page():
    return render_template("settings.html")

@app.route("/api/status")
def stream_status():
    def event_stream():
        while True:
            msg = status_queue.get()
            yield f"data: {msg}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/save_settings", methods=["POST"])
def save_settings():
    data = request.json
    os.makedirs("database", exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(data, f)
    return jsonify({"status": "success"})

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400
    
    # Nombre de archivo optimizado
    ext = os.path.splitext(file.filename)[1]
    tmp_name = f"NITRO_{uuid.uuid4().hex[:4]}{ext}"
    path = os.path.join("uploads", tmp_name)
    file.save(path)
    
    # Lanzar motor NITRO en segundo plano
    executor.submit(start_mally_engine, path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_nexus()
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
