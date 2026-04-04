import os, uuid, json, queue
from flask import Flask, render_template, request, jsonify, Response
from concurrent.futures import ThreadPoolExecutor
from config import init_nexus, DB_PATH
from bot import start_mally_engine

app = Flask(__name__)
# 50 hilos para que nunca se sature la comunicación
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
            # Recupera mensajes de la cola y los dispara a la web al instante
            msg = status_queue.get()
            yield f"data: {msg}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400
    
    # Nombre único para evitar conflictos de lectura/escritura
    path = os.path.join("uploads", f"ENT_{uuid.uuid4().hex[:5]}.mp4")
    file.save(path)
    
    # Ejecución inmediata en segundo plano
    executor.submit(start_mally_engine, path, file.filename, status_queue)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_nexus()
    app.run(host="0.0.0.0", port=8000, debug=False, threaded=True)
