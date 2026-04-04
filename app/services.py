import subprocess, os, threading, requests, time

BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHANNEL_ID = "-1003584710096"

class VideoEngine:
    @staticmethod
    def _fire(file_path):
        """Disparo de riel a Telegram"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        try:
            with open(file_path, 'rb') as v:
                r = requests.post(url, data={'chat_id': CHANNEL_ID}, files={'video': v}, timeout=600)
                if r.status_code == 200:
                    os.remove(file_path) # Desintegración post-envío
        except: pass

    @staticmethod
    def execute_parallel_cut(input_file, segment=60):
        # Obtener duración ultra-rápido
        cmd_dur = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        duration = float(subprocess.check_output(cmd_dur).decode().strip())

        out_dir = f"media/exports/V1T_{int(time.time())}"
        os.makedirs(out_dir, exist_ok=True)

        curr = 0
        idx = 1
        print(f"🌀 DESCOMPONIENDO ATÓMICAMENTE: {duration}s")

        while curr < duration:
            out = os.path.join(out_dir, f"atom_{idx:03d}.mp4")
            # COMANDO TURBO: Sin decodificación, sin latencia.
            f_cmd = ['ffmpeg', '-ss', str(curr), '-t', str(segment), '-i', input_file, '-c', 'copy', '-map', '0', '-y', out]
            subprocess.run(f_cmd, capture_output=True)
            
            # Hilo de subida paralelo
            threading.Thread(target=VideoEngine._fire, args=(out,), daemon=True).start()
            
            curr += segment
            idx += 1
            time.sleep(0.1) # Ráfaga controlada

        # Auto-limpieza del maestro
        threading.Timer(15, lambda: os.remove(input_file) if os.path.exists(input_file) else None).start()
