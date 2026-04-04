import subprocess, requests, os, time
from data import db
from logger import Logger

log = Logger()
OUT_DIR = "downloads"

def start_mally_engine(path, filename, s_queue):
    config = db.get()
    os.makedirs(OUT_DIR, exist_ok=True)
    
    base = os.path.splitext(filename)[0].replace("_", " ").upper()
    s_queue.put(f"⚡ PROCESANDO: {base}")
    log.info(f"Iniciando corte de {filename}")

    # FFmpeg: Corte por segmentos de 60s sin pérdida de calidad
    out_pattern = os.path.join(OUT_DIR, f"{base}_%03d.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", path, "-c", "copy", "-f", "segment", 
        "-segment_time", "60", "-reset_timestamps", "1", out_pattern
    ], capture_output=True)

    # Listar y ordenar alfabéticamente (001, 002, 003...)
    parts = sorted([f for f in os.listdir(OUT_DIR) if f.startswith(base)])
    total = len(parts)

    for i, p_name in enumerate(parts, 1):
        p_path = os.path.join(OUT_DIR, p_name)
        s_queue.put(f"📤 Enviando {i}/{total}...")

        caption = (
            f"🎬 **{base}**\n"
            f"📦 **PARTE:** {i} de {total}\n"
            f"👤 **AUTOR:** Noa\n"
            f"────────────────────\n"
            f"👑 **MALLY ENTERPRISE v16**"
        )

        try:
            with open(p_path, 'rb') as v:
                requests.post(
                    f"https://api.telegram.org/bot{config['bot_token']}/sendVideo",
                    data={'chat_id': config['chat_id'], 'caption': caption, 'parse_mode': 'Markdown'},
                    files={'video': v}, timeout=60
                )
            os.remove(p_path)
            time.sleep(0.4) # Blindaje de orden para ráfagas
        except Exception as e:
            log.error(f"Fallo en parte {i}: {e}")

    s_queue.put("✅ TRABAJO COMPLETADO")
    if os.path.exists(path): os.remove(path)
