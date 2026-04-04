import os, uuid, queue
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from data import db
from bot import start_mally_engine

app = Flask(__name__)
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
            msg = status_queue.get() # Espera infinita sin bloquear el servidor
            yield f"data: {msg}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/save_settings", methods=["POST"])
def save_settings():
    db.save(request.json)
    return jsonify({"status": "success"})

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400
    
    path = os.path.join("uploads", f"M_{uuid.uuid4().hex[:4]}.mp4")
    file.save(path)
    executor.submit(start_mally_engine, path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
