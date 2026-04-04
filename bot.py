import subprocess, requests, os, time
from data import db
from config import DOWNLOADS_DIR
from logger import log

def start_mally_engine(path, filename, s_queue):
    conf = db.get()
    token, cid = conf.get('bot_token'), conf.get('chat_id')

    if not token or not cid:
        s_queue.put("❌ ERROR: Configura el Token y ID")
        return

    base = os.path.splitext(filename)[0].upper().replace("_", " ")
    s_queue.put(f"🎬 PROCESANDO: {base}")
    
    # Corte ultra-rápido con FFmpeg
    out_pattern = os.path.join(DOWNLOADS_DIR, f"{base}_%03d.mp4")
    subprocess.run(["ffmpeg", "-y", "-i", path, "-c", "copy", "-map", "0", "-f", "segment", "-segment_time", "60", "-reset_timestamps", "1", out_pattern], capture_output=True)

    parts = sorted([f for f in os.listdir(DOWNLOADS_DIR) if f.startswith(base)])
    total = len(parts)

    for i, p in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOADS_DIR, p)
        s_queue.put(f"📤 Enviando {i}/{total}...")

        try:
            with open(p_path, 'rb') as v:
                r = requests.post(f"https://api.telegram.org/bot{token}/sendVideo", 
                    data={'chat_id': cid, 'caption': f"🎬 **{base}**\n📦 **PARTE:** {i}/{total}\n👑 **MALLY NITRO**", 'parse_mode': 'Markdown'}, 
                    files={'video': v}, timeout=100)
                
                if r.status_code != 200:
                    err = r.json().get('description', 'Error API')
                    s_queue.put(f"❌ FALLÓ: {err}")
                    break
        except Exception as e:
            s_queue.put(f"❌ ERROR RED: {str(e)[:15]}")
            break
        
        os.remove(p_path)
        time.sleep(0.5) # Pausa estratégica para orden 1,2,3

    s_queue.put("✅ PROCESO COMPLETADO")
    if os.path.exists(path): os.remove(path)
