import subprocess, requests, os, time
from config import get_nexus_settings, DOWNLOAD_FOLDER

def start_mally_engine(path, filename, s_queue):
    settings = get_nexus_settings()
    token, cid = settings.get("bot_token"), settings.get("chat_id")
    
    base_name = os.path.splitext(filename)[0].upper()
    out_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base_name}_%03d.mp4")

    s_queue.put(f"🎬 NITRO-CUT: {base_name}")

    # Corte FFmpeg Ultra-Rápido
    subprocess.run([
        "ffmpeg", "-y", "-i", path, "-c", "copy", "-f", "segment", 
        "-segment_time", "60", "-reset_timestamps", "1", out_pattern
    ], capture_output=True)

    # Listar y ORDENAR estrictamente
    parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base_title)])
    total = len(parts)

    for i, p_name in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
        s_queue.put(f"📤 Enviando Parte {i} de {total}...")

        caption = (
            f"🎬 **PELÍCULA:** {base_name}\n"
            f"📦 **PARTE:** {i}/{total}\n"
            f"👤 **CREADOR:** Noa\n"
            f"────────────────────\n"
            f"📢 @MallySeries | 👑 NITRO v14.5"
        )

        with open(p_path, 'rb') as v:
            # Envío secuencial rápido para asegurar orden 1,2,3
            requests.post(f"https://api.telegram.org/bot{token}/sendVideo", 
                data={'chat_id': cid, 'caption': caption, 'parse_mode': 'Markdown'}, 
                files={'video': v})
        
        os.remove(p_path)
        time.sleep(0.5) # Pausa mínima para que Telegram no mezcle el orden

    s_queue.put("✅ ORDEN COMPLETADO")
    if os.path.exists(path): os.remove(path)
