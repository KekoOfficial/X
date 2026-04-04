import subprocess
import os
import datetime
import requests
import threading
from concurrent.futures import ProcessPoolExecutor

# CONFIGURACIÓN DEL IMPERIO
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHANNEL_ID = "-1003584710096"

class VideoEngine:
    @staticmethod
    def _send_to_telegram(file_path):
        """Envía el clip al canal de forma asíncrona"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        try:
            with open(file_path, 'rb') as v:
                payload = {'chat_id': CHANNEL_ID, 'supports_streaming': 'true'}
                r = requests.post(url, data=payload, files={'video': v}, timeout=300)
                if r.status_code == 200:
                    os.remove(file_path) # Borrar clip enviado para ahorrar espacio
        except Exception as e:
            print(f"Error Telegram: {e}")

    @staticmethod
    def _cut_worker(input_file, start, duration, output):
        """Corte instantáneo mediante copia de stream"""
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-avoid_negative_ts', 'make_zero',
            '-map', '0', '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        # Disparar hilo de envío en cuanto el clip esté listo
        threading.Thread(target=VideoEngine._send_to_telegram, args=(output,)).start()
        return output

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        # Obtener duración real
        probe = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        total_sec = float(subprocess.check_output(probe).decode().strip())

        out_dir = os.path.join('media', 'exports', f"MALLY_{datetime.datetime.now().strftime('%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)

        tasks = []
        current = 0
        idx = 1
        while current < total_sec:
            out_path = os.path.join(out_dir, f"clip_{idx:03d}.mp4")
            tasks.append((input_file, current, segment_seconds, out_path))
            current += segment_seconds
            idx += 1

        # Ejecución en paralelo usando todos los núcleos de tu celular
        with ProcessPoolExecutor() as executor:
            executor.map(lambda p: VideoEngine._cut_worker(*p), tasks)

        # Limpiar video maestro al finalizar
        if os.path.exists(input_file):
            os.remove(input_file)
            
        return out_dir
