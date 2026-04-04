import os, uuid, queue
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from config.database import db
from app.services.bot_service import start_mally_engine

app = Flask(__name__, template_folder='../templates', static_folder='../static')
executor = ThreadPoolExecutor(max_workers=20)
status_queue = queue.Queue()

@app.route("/")
def index(): return render_template("upload.html")

@app.route("/api/status")
def stream_status():
    def event_stream():
        while True:
            yield f"data: {status_queue.get()}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    path = f"uploads/{uuid.uuid4().hex}.mp4"
    os.makedirs("uploads", exist_ok=True)
    file.save(path)
    executor.submit(start_mally_engine, path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
