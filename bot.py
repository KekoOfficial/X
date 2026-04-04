# bot.py - MOTOR MALLY v13
import subprocess, requests, os, time
from config import get_nexus_settings, DOWNLOAD_FOLDER

def start_mally_engine(path, filename):
    settings = get_nexus_settings()
    token = settings.get("bot_token")
    cid = settings.get("chat_id")

    if not token or not cid:
        return "ERROR: Configura el Token en Ajustes."

    base = os.path.splitext(filename)[0]
    output_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_part_%03d.mp4")

    # 1. Reporte al Canal
    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                  data={'chat_id': cid, 'text': f"🚀 **MALLY NEXUS v13**\n🎬 {filename}\n👑 Khassamx Dev", 'parse_mode': 'Markdown'})

    # 2. Fragmentación Flash
    cmd = ["ffmpeg", "-y", "-i", path, "-c", "copy", "-map", "0", "-f", "segment", "-segment_time", "60", "-reset_timestamps", "1", output_pattern]
    subprocess.run(cmd, capture_output=True)

    # 3. Envío Sincronizado
    parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
    for i, p in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOAD_FOLDER, p)
        with open(p_path, 'rb') as v:
            requests.post(f"https://api.telegram.org/bot{token}/sendVideo", 
                          data={'chat_id': cid, 'caption': f"📦 PARTE {i}/{len(parts)}\n📺 @MallySeries", 'supports_streaming': True}, 
                          files={'video': v})
        os.remove(p_path)
        time.sleep(1.2)
    
    if os.path.exists(path): os.remove(path)
