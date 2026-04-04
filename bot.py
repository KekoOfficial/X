import subprocess, requests, os, time
from config import get_nexus_settings, DOWNLOAD_FOLDER

def start_mally_engine(path, filename, s_queue):
    settings = get_nexus_settings()
    token, cid = settings.get("bot_token"), settings.get("chat_id")
    if not token or not cid: return

    base = os.path.splitext(filename)[0]
    out_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base}_%03d.mp4")

    # 1. Mensaje Maestro en Telegram
    s_queue.put(f"🎬 Analizando: {filename}")
    res = requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
          data={'chat_id': cid, 'text': f"⏳ **MALLY MONITOR v14**\n🛰️ Procesando: {filename}\n📦 Preparando fragmentos...", 'parse_mode': 'Markdown'})
    msg_id = res.json()['result']['message_id']

    # 2. Corte Flash FFmpeg
    subprocess.run(["ffmpeg", "-y", "-i", path, "-c", "copy", "-map", "0", "-f", "segment", "-segment_time", "60", "-reset_timestamps", "1", out_pattern], capture_output=True)

    parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base)])
    total = len(parts)

    # 3. Envío y Monitoreo
    for i, p in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOAD_FOLDER, p)
        s_queue.put(f"📤 Enviando Parte {i}/{total}")
        
        # Editamos mensaje maestro en Telegram
        requests.post(f"https://api.telegram.org/bot{token}/editMessageText", 
            data={'chat_id': cid, 'message_id': msg_id, 'text': f"⚡ **ENVIANDO:** {filename}\n📦 Parte: {i} de {total}\n🔥 @MallySeries", 'parse_mode': 'Markdown'})

        with open(p_path, 'rb') as v:
            requests.post(f"https://api.telegram.org/bot{token}/sendVideo", data={'chat_id': cid, 'supports_streaming': True}, files={'video': v})
        
        os.remove(p_path)
        time.sleep(1)
    
    s_queue.put("✅ PROCESO COMPLETADO")
    requests.post(f"https://api.telegram.org/bot{token}/editMessageText", 
        data={'chat_id': cid, 'message_id': msg_id, 'text': f"✅ **FINALIZADO:** {filename}\n🎬 Total: {total} partes enviadas.\n👑 Khassamx Dev", 'parse_mode': 'Markdown'})
    if os.path.exists(path): os.remove(path)
