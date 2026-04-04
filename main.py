import os, json, uuid, subprocess, requests, time
from flask import Flask, request, render_template, jsonify
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
DB_PATH = "database/settings.json"
executor = ThreadPoolExecutor(max_workers=10)

# Cargar configuración desde la base de datos local
def get_config():
    if not os.path.exists(DB_PATH):
        return {"bot_token": "", "chat_id": ""}
    with open(DB_PATH, "r") as f:
        return json.load(f)

@app.route("/api/save_settings", methods=["POST"])
def save_settings():
    data = request.json
    os.makedirs("database", exist_ok=True)
    with open(DB_PATH, "w") as f:
        json.dump(data, f)
    return jsonify({"status": "⚙️ Configuración Mally Guardada"})

def mally_nexus_engine(input_path, filename):
    config = get_config()
    token = config.get("bot_token")
    cid = config.get("chat_id")
    
    if not token or not cid:
        return # No procesa si no hay ajustes configurados

    base = os.path.splitext(filename)[0]
    output_pattern = f"downloads/{base}_part_%03d.mp4"
    
    try:
        # Reporte de Inicio con los datos cargados dinámicamente
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      data={'chat_id': cid, 'text': f"🚀 **MALLY NEXUS v13: INICIANDO**\n🎬 {filename}\n👑 Khassamx Dev", 'parse_mode': 'Markdown'})

        # Motor Flash (Corte de 1 min)
        cmd = ["ffmpeg", "-y", "-i", input_path, "-c", "copy", "-map", "0", "-f", "segment", "-segment_time", "60", "-reset_timestamps", "1", output_pattern]
        subprocess.run(cmd, capture_output=True)

        parts = sorted([f for f in os.listdir("downloads") if f.startswith(base)])
        for i, p_name in enumerate(parts, 1):
            with open(f"downloads/{p_name}", 'rb') as v:
                requests.post(f"https://api.telegram.org/bot{token}/sendVideo", 
                              data={'chat_id': cid, 'caption': f"📦 PARTE {i}/{len(parts)}\n📺 @MallySeries", 'supports_streaming': True}, 
                              files={'video': v})
            os.remove(f"downloads/{p_name}")
            time.sleep(1.2)

        if os.path.exists(input_path): os.remove(input_path)
    except Exception as e:
        print(f"Error: {e}")

@app.route("/")
def index(): return render_template("upload.html")

@app.route("/api/upload_mally", methods=["POST"])
def upload():
    file = request.files.get("video")
    path = f"uploads/V13_{uuid.uuid4().hex[:5]}_{file.filename}"
    file.save(path)
    executor.submit(mally_nexus_engine, path, file.filename)
    return jsonify({"status": "success"})

if __name__ == "__main__":
    for d in ["uploads", "downloads", "database"]: os.makedirs(d, exist_ok=True)
    app.run(host="0.0.0.0", port=8000, debug=False)
