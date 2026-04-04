import subprocess, requests, os
from config import get_nexus_settings, DOWNLOAD_FOLDER
from concurrent.futures import ThreadPoolExecutor

def start_mally_engine(path, filename, s_queue):
    settings = get_nexus_settings()
    token, cid = settings.get("bot_token"), settings.get("chat_id")
    
    if not token or not cid:
        s_queue.put("❌ ERROR: Configura los Tokens")
        return

    # Título limpio y formateado
    base_name = os.path.splitext(filename)[0].replace("_", " ").upper()
    out_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base_name}_%03d.mp4")

    # --- CORTE ULTRA-VELOZ ---
    s_queue.put(f"⚡ NITRO-CUT: {base_name}")
    subprocess.run([
        "ffmpeg", "-y", "-i", path, 
        "-c", "copy", "-map", "0", 
        "-f", "segment", "-segment_time", "60", 
        "-reset_timestamps", "1", "-break_non_keyframes", "1",
        out_pattern
    ], capture_output=True)

    parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base_name)])
    total = len(parts)
    s_queue.put(f"🚀 ENVIANDO {total} PARTES EN RÁFAGA...")

    # Función interna de envío simultáneo
    def dispatch_video(args):
        i, p = args
        p_path = os.path.join(DOWNLOAD_FOLDER, p)
        
        caption_text = (
            f"🎬 **PELÍCULA:** {base_name}\n"
            f"📦 **PARTE:** {i} de {total}\n"
            f"👤 **CREADOR:** Khassamx Dev\n"
            f"────────────────────\n"
            f"📸 **Instagram:** @MallySeries\n"
            f"🎵 **TikTok:** @Esenaen15\n"
            f"📢 **Telegram:** @MallySeries\n"
            f"────────────────────\n"
            f"👑 **IMPERIO MALLY v14.5 NITRO**"
        )

        try:
            with open(p_path, 'rb') as v:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendVideo", 
                    data={
                        'chat_id': cid, 
                        'caption': caption_text, 
                        'parse_mode': 'Markdown',
                        'supports_streaming': True
                    }, 
                    files={'video': v},
                    timeout=60
                )
            os.remove(p_path)
        except:
            pass

    # --- ENVÍO MULTI-HILO (Envía 5 videos a la vez) ---
    with ThreadPoolExecutor(max_workers=5) as burst_executor:
        burst_executor.map(dispatch_video, enumerate(parts, 1))

    s_queue.put("✅ ¡RÁFAGA COMPLETADA CON ÉXITO!")
    if os.path.exists(path): os.remove(path)
