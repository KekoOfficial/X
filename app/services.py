import subprocess
import os
import datetime
import requests
import threading
import time
from concurrent.futures import ProcessPoolExecutor
from queue import Queue

# --- PROTOCOLO IMPERIAL V20 ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHANNEL_ID = "-1003584710096"

class VideoEngine:
    # Cola de subida para no saturar la conexión
    upload_queue = Queue()

    @staticmethod
    def _uploader_thread():
        """Hilo dedicado exclusivamente a bombardeo de Telegram"""
        while True:
            file_path = VideoEngine.upload_queue.get()
            if file_path is None: break
            
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
            filename = os.path.basename(file_path)
            
            # Reintentos automáticos si falla el internet
            for attempt in range(3):
                try:
                    with open(file_path, 'rb') as v:
                        payload = {'chat_id': CHANNEL_ID, 'supports_streaming': 'true'}
                        r = requests.post(url, data=payload, files={'video': v}, timeout=300)
                        if r.status_code == 200:
                            print(f"✅ DISPARADO: {filename}")
                            os.remove(file_path) # Limpieza inmediata
                            break
                except Exception as e:
                    print(f"⚠️ Reintento {attempt+1} para {filename}: {e}")
                    time.sleep(5)
            
            VideoEngine.upload_queue.task_done()

    @staticmethod
    def _cut_worker(input_file, start, duration, output):
        """Corte quirúrgico con prioridad de proceso"""
        # Usamos '-map 0' y '-c copy' para mantener calidad original a velocidad luz
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-map', '0',
            '-avoid_negative_ts', 'make_zero', '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        
        # Encolar para subida inmediata
        VideoEngine.upload_queue.put(output)
        return output

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        # 1. Iniciar el hilo de subida si no está vivo
        upload_worker = threading.Thread(target=VideoEngine._uploader_thread, daemon=True)
        upload_worker.start()

        # 2. Análisis de metadatos ultra-rápido
        probe = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        total_sec = float(subprocess.check_output(probe).decode().strip())

        # 3. Directorio Nitro
        out_dir = os.path.join('media', 'exports', f"MASTER_{datetime.datetime.now().strftime('%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)

        # 4. Preparar fragmentación
        tasks = []
        current = 0
        idx = 1
        while current < total_sec:
            out_path = os.path.join(out_dir, f"part_{idx:03d}.mp4")
            tasks.append((input_file, current, segment_seconds, out_path))
            current += segment_seconds
            idx += 1

        # 5. POTENCIA MULTI-NÚCLEO (Limitado para no calentar el móvil)
        print(f"🔥 INICIANDO FRAGMENTACIÓN: {len(tasks)} CLIPS EN COLA")
        with ProcessPoolExecutor(max_workers=3) as executor:
            list(executor.map(lambda p: VideoEngine._cut_worker(*p), tasks))

        # 6. CIERRE SEGURO: Borrar maestro original para liberar espacio brutal
        if os.path.exists(input_file):
            os.remove(input_file)
            print("🗑️ Memoria liberada: Video maestro eliminado.")

        return out_dir
