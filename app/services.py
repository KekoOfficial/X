import subprocess
import os
import datetime
import requests
import threading
import time
from queue import Queue

# --- PROTOCOLO IMPERIAL V21 ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHANNEL_ID = "-1003584710096"

class VideoEngine:
    upload_queue = Queue()

    @staticmethod
    def _uploader_thread():
        """Hilo de bombardeo constante a Telegram"""
        while True:
            file_path = VideoEngine.upload_queue.get()
            if file_path is None: break
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
            try:
                with open(file_path, 'rb') as v:
                    payload = {'chat_id': CHANNEL_ID, 'supports_streaming': 'true'}
                    r = requests.post(url, data=payload, files={'video': v}, timeout=300)
                    if r.status_code == 200:
                        print(f"✅ CLIP ENVIADO: {os.path.basename(file_path)}")
                        os.remove(file_path) # Limpieza inmediata
            except Exception as e:
                print(f"⚠️ Error subida: {e}")
            
            VideoEngine.upload_queue.task_done()

    @staticmethod
    def _run_ffmpeg(task):
        """Ejecuta el corte físico"""
        input_file, start, duration, output = task
        # '-c copy' es el secreto de la velocidad
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-map', '0',
            '-avoid_negative_ts', 'make_zero', '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        VideoEngine.upload_queue.put(output)

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        # 1. Iniciar uploader
        threading.Thread(target=VideoEngine._uploader_thread, daemon=True).start()

        # 2. Obtener duración real
        probe = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        total_sec = float(subprocess.check_output(probe).decode().strip())

        # 3. Preparar salida
        out_dir = os.path.join('media', 'exports', f"MALLY_{datetime.datetime.now().strftime('%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)

        # 4. Lanzar ráfaga de cortes
        current = 0
        idx = 1
        print(f"🔥 DISPARANDO MOTOR: Fragmentando video de {total_sec}s...")
        
        while current < total_sec:
            out_path = os.path.join(out_dir, f"clip_{idx:03d}.mp4")
            task = (input_file, current, segment_seconds, out_path)
            
            # Lanzamos cada corte en un hilo. 
            # Como usamos '-c copy', el CPU casi no sufre, solo el disco.
            threading.Thread(target=VideoEngine._run_ffmpeg, args=(task,)).start()
            
            current += segment_seconds
            idx += 1
            # Pequeña pausa para no saturar el sistema de archivos de Android
            time.sleep(0.5)

        # 5. Esperar un poco antes de borrar el maestro (seguridad)
        # En una versión avanzada, borraríamos el maestro después de que la cola esté vacía.
        return out_dir
