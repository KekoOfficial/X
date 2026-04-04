import subprocess, requests, os, time
from config import get_nexus_settings, DOWNLOAD_FOLDER

def start_mally_engine(path, filename, s_queue):
    settings = get_nexus_settings()
    token, cid = settings.get("bot_token"), settings.get("chat_id")
    
    # Limpiamos el nombre para el branding imperial
    base_name = os.path.splitext(filename)[0].replace("_", " ").upper()
    out_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base_name}_%03d.mp4")

    s_queue.put(f"⚡ NITRO-CUT: {base_name}")

    # CORTE INSTANTÁNEO (Sin re-codificar para máxima velocidad)
    subprocess.run([
        "ffmpeg", "-y", "-i", path, "-c", "copy", "-map", "0", 
        "-f", "segment", "-segment_time", "60", "-reset_timestamps", "1", 
        out_pattern
    ], capture_output=True)

    # Ordenamos alfabéticamente para asegurar 001, 002, 003...
    parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base_name)])
    total = len(parts)

    s_queue.put(f"🚀 ENVIANDO {total} PARTES...")

    for i, p_name in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
        
        # Aviso rápido a la web
        s_queue.put(f"📦 Enviando {i}/{total}")

        caption = (
            f"🎬 **PELÍCULA:** {base_name}\n"
            f"📦 **PARTE:** {i} de {total}\n"
            f"👤 **CREADOR:** Noa\n"
            f"────────────────────\n"
            f"📢 @MallySeries | 📸 @MallySeries\n"
            f"👑 **ENTERPRISE v15.2**"
        )

        with open(p_path, 'rb') as v:
            # Envío directo. Telegram procesa el orden por tiempo de llegada.
            requests.post(
                f"https://api.telegram.org/bot{token}/sendVideo", 
                data={'chat_id': cid, 'caption': caption, 'parse_mode': 'Markdown', 'supports_streaming': True}, 
                files={'video': v}
            )
        
        os.remove(p_path)
        # Pausa mínima de 0.2s para que Telegram no mezcle los mensajes
        time.sleep(0.2)

    s_queue.put("✅ PROCESO COMPLETADO")
    if os.path.exists(path): os.remove(path)
