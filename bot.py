import subprocess, requests, os
from config import get_nexus_settings, DOWNLOAD_FOLDER
from concurrent.futures import ThreadPoolExecutor

def start_mally_engine(path, filename, s_queue):
    settings = get_nexus_settings()
    token, cid = settings.get("bot_token"), settings.get("chat_id")
    
    if not token or not cid:
        s_queue.put("❌ CONFIGURACIÓN INCOMPLETA")
        return

    # Formatear título imperial
    base_title = os.path.splitext(filename)[0].replace("_", " ").upper()
    out_pattern = os.path.join(DOWNLOAD_FOLDER, f"{base_title}_%03d.mp4")

    # Notificar a la Web
    s_queue.put(f"⚡ NITRO-CUT: {base_title}")

    # FFmpeg optimizado para fragmentar sin procesar (Instantáneo)
    subprocess.run([
        "ffmpeg", "-y", "-i", path, 
        "-c", "copy", "-f", "segment", "-segment_time", "60", 
        "-reset_timestamps", "1", out_pattern
    ], capture_output=True)

    # Identificar fragmentos creados
    parts = sorted([f for f in os.listdir(DOWNLOAD_FOLDER) if f.startswith(base_title)])
    total = len(parts)

    if total == 0:
        s_queue.put("❌ ERROR: FFmpeg no generó archivos")
        return

    s_queue.put(f"🚀 ENVIANDO {total} PARTES EN RÁFAGA...")

    # Función de envío atómico
    def send_burst(data):
        i, p_name = data
        p_path = os.path.join(DOWNLOAD_FOLDER, p_name)
        
        caption = (
            f"🎬 **PELÍCULA:** {base_title}\n"
            f"📦 **PARTE:** {i} de {total}\n"
            f"👤 **CREADOR:** Noa\n"
            f"────────────────────\n"
            f"📸 **Instagram:** @MallySeries\n"
            f"🎵 **TikTok:** @Esenaen15\n"
            f"📢 **Telegram:** @MallySeries\n"
            f"────────────────────\n"
            f"👑 **NITRO v14.5**"
        )

        try:
            with open(p_path, 'rb') as v:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendVideo", 
                    data={
                        'chat_id': cid, 
                        'caption': caption, 
                        'parse_mode': 'Markdown',
                        'supports_streaming': True
                    }, 
                    files={'video': v},
                    timeout=60
                )
            os.remove(p_path)
        except Exception as e:
            print(f"Error en envío de parte {i}: {e}")

    # Envío paralelo controlado (3 hilos simultáneos)
    with ThreadPoolExecutor(max_workers=3) as nitro_executor:
        nitro_executor.map(send_burst, enumerate(parts, 1))

    s_queue.put("✅ RÁFAGA COMPLETADA")
    
    # Limpiar video maestro
    if os.path.exists(path): os.remove(path)
