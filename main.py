import os, uuid, json, queue
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from config import init_nexus, DB_PATH
from bot import start_mally_engine
from logger import Logger

app = Flask(__name__)
log = Logger()
executor = ThreadPoolExecutor(max_workers=10)
status_queue = queue.Queue() # Cola para mensajes en tiempo real

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
    path = os.path.join("uploads", f"V14_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    # Enviamos el trabajo al motor
    executor.submit(start_mally_engine, path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_nexus()
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
