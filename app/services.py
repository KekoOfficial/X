import subprocess
import os
import datetime
import requests
import threading
from concurrent.futures import ProcessPoolExecutor

# --- CREDENCIALES DEL IMPERIO MP ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHANNEL_ID = "-1003584710096"

class VideoEngine:
    @staticmethod
    def _telegram_sender(file_path):
        """Hilo de envío: Sube a Telegram sin detener el motor de corte"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        filename = os.path.basename(file_path)
        
        try:
            with open(file_path, 'rb') as v:
                payload = {
                    'chat_id': CHANNEL_ID, 
                    'caption': f"🎬 Clip: {filename}\n🚀 @ImperioMP_Bot",
                    'supports_streaming': 'true'
                }
                # Enviamos el video
                response = requests.post(url, data=payload, files={'video': v}, timeout=300)
                
                if response.status_code == 200:
                    print(f"✅ DISPARADO CON ÉXITO: {filename}")
                    # Limpieza automática: Borra el clip para no llenar tu Termux
                    os.remove(file_path)
                else:
                    print(f"⚠️ Error Telegram ({response.status_code}): {response.text}")
        
        except Exception as e:
            print(f"❌ FALLO CRÍTICO EN ENVÍO: {e}")

    @staticmethod
    def _ffmpeg_worker(input_file, start, duration, output):
        """Corte físico a máxima velocidad (Stream Copy)"""
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-avoid_negative_ts', 'make_zero',
            output, '-y'
        ]
        # Ejecuta el corte
        subprocess.run(cmd, capture_output=True)
        
        # En cuanto termina este segmento, lanzamos el envío en un hilo independiente
        threading.Thread(target=VideoEngine._telegram_sender, args=(output,)).start()
        return output

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        # 1. Obtener duración (Hiper-rápido con ffprobe)
        probe = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        total_sec = float(subprocess.check_output(probe).decode().strip())

        # 2. Carpeta de salida única
        folder_name = f"MALLY_UP_{datetime.datetime.now().strftime('%H%M%S')}"
        out_dir = os.path.join('media', 'exports', folder_name)
        os.makedirs(out_dir, exist_ok=True)

        # 3. Planificación de ráfaga (60s por clip)
        tasks = []
        current = 0
        idx = 1
        while current < total_sec:
            out_path = os.path.join(out_dir, f"clip_{idx:03d}.mp4")
            tasks.append((input_file, current, segment_seconds, out_path))
            current += segment_seconds
            idx += 1

        # 4. LANZAMIENTO NITRO
        print(f"🔥 MODO IMPERIAL: Fragmentando y Enviando {len(tasks)} partes...")
        
        # Usamos ProcessPoolExecutor para el corte (CPU) 
        # y threads internos para la subida (Red)
        with ProcessPoolExecutor() as executor:
            executor.map(lambda p: VideoEngine._ffmpeg_worker(*p), tasks)

        # 5. Limpiar el video maestro original de 'media/raw' para ahorrar GBs
        try:
            os.remove(input_file)
            print(f"🗑️ Video maestro eliminado para optimizar espacio.")
        except:
            pass

        return out_dir
