import subprocess, requests, os, time
from config.settings import DOWNLOADS_DIR

def run_video_engine(path, filename, s_queue, token, chat_id):
    base_name = os.path.splitext(filename)[0].upper().replace("_", " ")
    s_queue.put(f"🎬 PROCESANDO: {base_name}")
    
    # Corte con FFmpeg (Segmentos de 60s)
    output_pattern = os.path.join(DOWNLOADS_DIR, f"{base_name}_%03d.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", path, "-c", "copy", "-map", "0", 
        "-f", "segment", "-segment_time", "60", "-reset_timestamps", "1", output_pattern
    ], capture_output=True)

    parts = sorted([f for f in os.listdir(DOWNLOADS_DIR) if f.startswith(base_name)])
    total = len(parts)

    for i, p_name in enumerate(parts, 1):
        p_path = os.path.join(DOWNLOADS_DIR, p_name)
        s_queue.put(f"📤 Enviando {i}/{total}...")

        with open(p_path, 'rb') as video_file:
            requests.post(
                f"https://api.telegram.org/bot{token}/sendVideo",
                data={'chat_id': chat_id, 'caption': f"🎬 **{base_name}**\n📦 **PARTE:** {i}/{total}\n👑 **MALLY ENTERPRISE**", 'parse_mode': 'Markdown'},
                files={'video': video_file}
            )
        os.remove(p_path)
        time.sleep(0.5) # Evita el bloqueo de Telegram

    s_queue.put("✅ TRABAJO COMPLETADO")
    if os.path.exists(path): os.remove(path)
