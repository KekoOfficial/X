import os, uuid, queue
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from data import db
from bot import start_mally_engine
from logger import Logger

app = Flask(__name__)
log = Logger()
executor = ThreadPoolExecutor(max_workers=50)
status_queue = queue.Queue()

@app.route("/")
def index(): return render_template("upload.html")

@app.route("/settings")
def settings_page(): return render_template("settings.html")

@app.route("/api/status")
def stream_status():
    def event_stream():
        while True:
            yield f"data: {status_queue.get()}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/save_settings", methods=["POST"])
def save_settings():
    db.save(request.json)
    log.info("Configuración actualizada en NexusDB")
    return jsonify({"status": "success"})

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400
    
    path = os.path.join("uploads", f"ENT_{uuid.uuid4().hex[:4]}.mp4")
    os.makedirs("uploads", exist_ok=True)
    file.save(path)
    
    executor.submit(start_mally_engine, path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
