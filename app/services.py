import subprocess
import os
import datetime
import requests
import threading
import time

# --- CONFIGURACIÓN DIRECTA ---
BOT_TOKEN = "8759783698:AAFUuC67X--qXoqD4D2YQ7RYlPlHoQmoYlU"
CHANNEL_ID = "-1003584710096"

class VideoEngine:
    @staticmethod
    def _enviar_a_telegram(archivo):
        """Envía al canal y borra el fragmento al terminar"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        try:
            with open(archivo, 'rb') as v:
                payload = {'chat_id': CHANNEL_ID, 'supports_streaming': 'true'}
                r = requests.post(url, data=payload, files={'video': v}, timeout=300)
                if r.status_code == 200:
                    print(f"✅ ENVIADO: {os.path.basename(archivo)}")
                    os.remove(archivo) # Limpieza para no llenar el cel
        except Exception as e:
            print(f"❌ Error en envío: {e}")

    @staticmethod
    def _cortar_y_subir(input_file, start, duration, output):
        """Corte rápido y dispara el hilo de subida"""
        # Usamos '-c copy' porque es lo único que garantiza velocidad instantánea
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-map', '0',
            '-avoid_negative_ts', 'make_zero', '-y', output
        ]
        subprocess.run(cmd, capture_output=True)
        # En cuanto se corta, se dispara la subida en su propio hilo
        threading.Thread(target=VideoEngine._enviar_a_telegram, args=(output,)).start()

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        # 1. Analizar duración
        probe = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_file]
        total_sec = float(subprocess.check_output(probe).decode().strip())

        # 2. Carpeta de salida
        out_dir = os.path.join('media', 'exports', f"MALLY_{datetime.datetime.now().strftime('%H%M%S')}")
        os.makedirs(out_dir, exist_ok=True)

        current = 0
        idx = 1
        print(f"🔥 INICIANDO CORTE: {input_file}")

        # 3. Bucle de disparo
        while current < total_sec:
            out_path = os.path.join(out_dir, f"clip_{idx:03d}.mp4")
            # Ejecutamos el corte
            VideoEngine._cortar_y_subir(input_file, current, segment_seconds, out_path)
            
            current += segment_seconds
            idx += 1
            # Pausa de medio segundo para que el disco de Android respire
            time.sleep(0.5)

        # 4. Borrar el video original de 10 horas para recuperar espacio
        # Lo hacemos después de un pequeño delay para asegurar que FFmpeg soltó el archivo
        def limpieza_maestra():
            time.sleep(10)
            if os.path.exists(input_file):
                os.remove(input_file)
                print("🗑️ Maestro eliminado. Memoria libre.")
        
        threading.Thread(target=limpieza_maestra).start()
