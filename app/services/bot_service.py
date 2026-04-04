import subprocess, requests, os, time
from config.database import db
from utils.logger import log

def start_mally_engine(path, filename, s_queue):
    config = db.get_config()
    token, cid = config.get('bot_token'), config.get('chat_id')

    base = os.path.splitext(filename)[0].upper()
    s_queue.put(f"🚀 INICIANDO: {base}")

    # Corte Nitro
    out_pattern = f"downloads/{base}_%03d.mp4"
    os.makedirs("downloads", exist_ok=True)
    
    subprocess.run(["ffmpeg", "-y", "-i", path, "-c", "copy", "-f", "segment", "-segment_time", "60", "-reset_timestamps", "1", out_pattern], capture_output=True)

    parts = sorted([f for f in os.listdir("downloads") if f.startswith(base)])
    total = len(parts)

    for i, p in enumerate(parts, 1):
        p_path = os.path.join("downloads", p)
        s_queue.put(f"📤 Enviando {i}/{total}...")
        
        with open(p_path, 'rb') as v:
            requests.post(f"https://api.telegram.org/bot{token}/sendVideo", 
                         data={'chat_id': cid, 'caption': f"🎬 **{base}**\n📦 **PARTE:** {i}/{total}\n👤 **AUTOR:** Noa", 'parse_mode': 'Markdown'}, 
                         files={'video': v})
        
        os.remove(p_path)
        time.sleep(0.4) # Garantiza orden 1, 2, 3

    s_queue.put("✅ PROCESO COMPLETADO")
    if os.path.exists(path): os.remove(path)
