import subprocess, requests, os, time
from config.database import db
from config.settings import DOWNLOADS_DIR

def run_mally_engine(path, filename, s_queue):
    conf = db.get_config()
    base = os.path.splitext(filename)[0].upper().replace("_", " ")
    
    # Notificación de inicio
    s_queue.put(f"⚡ INICIANDO CORTE: {base}")
    
    out_pattern = os.path.join(DOWNLOADS_DIR, f"{base}_%03d.mp4")
    
    # Corte instantáneo con FFmpeg
    subprocess.run(["ffmpeg", "-y", "-i", path, "-c", "copy", "-f", "segment", 
                    "-segment_time", "60", "-reset_timestamps", "1", out_pattern], capture_output=True)

    parts = sorted([f for f in os.listdir(DOWNLOADS_DIR) if f.startswith(base)])
    total = len(parts)

    for i, p in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOADS_DIR, p)
        s_queue.put(f"📤 Enviando {i}/{total}...") # Esto actualiza tu barra de progreso

        with open(p_path, 'rb') as v:
            requests.post(f"https://api.telegram.org/bot{conf['bot_token']}/sendVideo", 
                         data={'chat_id': conf['chat_id'], 'caption': f"🎬 **{base}**\n📦 **PARTE:** {i}/{total}", 'parse_mode': 'Markdown'}, 
                         files={'video': v})
        
        os.remove(p_path)
        time.sleep(0.4) # Garantiza el orden 1, 2, 3

    s_queue.put("✅ PROCESO COMPLETADO")
    if os.path.exists(path): os.remove(path)
