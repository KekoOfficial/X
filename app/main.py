from flask import Flask, render_template, Response, request, jsonify
import os, uuid, queue
from concurrent.futures import ThreadPoolExecutor
from app.services.bot_service import run_video_engine
from dotenv import load_dotenv

load_dotenv() # Carga BOT_TOKEN y CHAT_ID desde .env

app = Flask(__name__, 
            template_folder='../templates', 
            static_folder='../static')

executor = ThreadPoolExecutor(max_workers=10)
status_queue = queue.Queue()

# --- RUTAS DE NAVEGACIÓN (MALLYWEAR / MALLYCUTS) ---
@app.route("/")
def index(): return render_template("index.html")

@app.route("/shop")
def shop(): return render_template("shop.html")

@app.route("/product")
def product(): return render_template("product.html")

@app.route("/contact")
def contact(): return render_template("contact.html")

@app.route("/about")
def about(): return render_template("about.html")

# --- API DE PROCESAMIENTO ---
@app.route("/api/status")
def status_stream():
    def event_stream():
        while True:
            yield f"data: {status_queue.get()}\n\n"
    return Response(event_stream(), mimetype="text/event-stream")

@app.route("/api/upload", methods=["POST"])
def upload_video():
    file = request.files.get("video")
    if not file: return jsonify({"error": "No file"}), 400
    
    save_path = os.path.join("uploads", f"{uuid.uuid4().hex}.mp4")
    file.save(save_path)
    
    # Lanza el bot en segundo plano
    executor.submit(run_video_engine, save_path, file.filename, status_queue, 
                    os.getenv("BOT_TOKEN"), os.getenv("CHAT_ID"))
    return jsonify({"status": "success"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
