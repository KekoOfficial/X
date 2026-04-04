# main.py - LANZADOR NEXUS v13
import os, uuid, json
from flask import Flask, render_template, request, jsonify
from concurrent.futures import ThreadPoolExecutor
from config import init_nexus, DB_PATH
from bot import start_mally_engine
from logger import Logger

app = Flask(__name__)
log = Logger()
executor = ThreadPoolExecutor(max_workers=10)

@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/api/save_settings", methods=["POST"])
def save_settings():
    data = request.json
    with open(DB_PATH, "w") as f:
        json.dump(data, f)
    log.success("Ajustes NEXUS actualizados.")
    return jsonify({"status": "success"})

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    if not file: return jsonify({"status": "error"}), 400
    
    path = os.path.join("uploads", f"V13_{uuid.uuid4().hex[:5]}_{file.filename}")
    file.save(path)
    
    log.info(f"Procesando: {file.filename}")
    executor.submit(start_mally_engine, path, file.filename)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    init_nexus()
    log.info("🛡️ CONSOLA MALLY NEXUS v13 ONLINE")
    app.run(host="0.0.0.0", port=8000, debug=False)
