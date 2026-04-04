import subprocess
import os
import datetime
import requests
import threading
import time
from queue import Queue

# --- PROTOCOLO DE CONEXIÓN IMPERIAL ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHANNEL_ID = "-1003584710096"

class VideoEngine:
    # Cola de subida sincronizada (Thread-Safe)
    upload_queue = Queue()
    is_uploader_active = False

    @staticmethod
    def _uploader_logic():
        """Hilo de bombardeo constante: No se detiene hasta vaciar la cola"""
        while True:
            file_path = VideoEngine.upload_queue.get()
            if file_path is None: break
            
            filename = os.path.basename(file_path)
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
            
            # Sistema de Reintentos V2000 (3 intentos con pausa progresiva)
            for attempt in range(3):
                try:
                    with open(file_path, 'rb') as v:
                        payload = {'chat_id': CHANNEL_ID, 'supports_streaming': 'true'}
                        r = requests.post(url, data=payload, files={'video': v}, timeout=300)
                        if r.status_code == 200:
                            print(f"✅ V2000 DISPARADO: {filename}")
                            os.remove(file_path) # Limpieza instantánea para liberar memoria
                            break
                        else:
                            print(f"⚠️ Error {r.status_code} en {filename}. Reintentando...")
                except Exception as e:
                    print(f"❌ Fallo de red en {filename}: {e}")
                time.sleep(5 * (attempt + 1)) # Pausa inteligente
            
            VideoEngine.upload_queue.task_done()

    @staticmethod
    def _cut_worker(task):
        """Corte quirúrgico con optimización de hardware"""
        input_file, start, duration, output = task
        # Comando Nitro: -c copy para no usar CPU, -avoid_negative_ts para evitar lag en Telegram
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-map', '0',
            '-avoid_negative_ts', 'make_zero', '-y', output
        ]
        # Ejecución silenciosa para no saturar los logs de Termux
        subprocess.run(cmd, capture_output=True)
        
        # Inyectar en la cola de subida inmediatamente
        VideoEngine.upload_queue.put(output)

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        """Orquestador de la Matriz V2000"""
        
        # 1. Activar Uploader si está dormido
        if not VideoEngine.is_uploader_active:
            t = threading.Thread(target=VideoEngine._uploader_logic, daemon=True)
            t.start()
            VideoEngine.is_uploader_active = True

        # 2. Análisis de Metadatos Real-Time
        probe = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        try:
            total_sec = float(subprocess.check_output(probe).decode().strip())
        except Exception as e:
            print(f"🛑 Error de lectura: {e}")
            return

        # 3. Creación de entorno de exportación
        out_dir = os.path.join('media', 'exports', f"V2K_{datetime.datetime.now().strftime('%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)

        # 4. DISPARO DE RÁFAGA (Corte Lineal con Envío Paralelo)
        current = 0
        idx = 1
        print(f"🔥 V2000 ACTIVADO | FRAGMENTANDO {total_sec} SEG...")

        while current < total_sec:
            out_path = os.path.join(out_dir, f"mally_part_{idx:03d}.mp4")
            task = (input_file, current, segment_seconds, out_path)
            
            # Lanzamos el corte en un hilo independiente
            threading.Thread(target=VideoEngine._cut_worker, args=(task,)).start()
            
            current += segment_seconds
            idx += 1
            # Delay de seguridad para que el disco de Android no colapse (I/O Throttle)
            time.sleep(0.3)

        # 5. AUTO-DESTRUCCIÓN DE SEGURIDAD (Limpieza del video de 10 horas)
        def cleanup():
            # Esperamos a que la cola esté casi vacía para no borrar el archivo mientras se lee
            time.sleep(30) 
            if os.path.exists(input_file):
                os.remove(input_file)
                print("🗑️ V2000: Video maestro eliminado. Espacio recuperado.")

        threading.Thread(target=cleanup, daemon=True).start()
        return out_dir
