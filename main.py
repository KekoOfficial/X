import os, uuid, json, queue
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from config import init_nexus, DB_PATH
from bot import start_mally_engine

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=20)
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

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400
    
    path = os.path.join("uploads", f"V14_{uuid.uuid4().hex[:4]}.mp4")
    file.save(path)
    
    executor.submit(start_mally_engine, path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_nexus()
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
