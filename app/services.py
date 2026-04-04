import subprocess
import os
import datetime
import requests
from concurrent.futures import ProcessPoolExecutor

# --- CONFIGURACIÓN IMPERIAL ---
BOT_TOKEN = "TU_TOKEN_DE_BOT_AQUÍ"
CHANNEL_ID = "@TU_CANAL_O_ID" # Ejemplo: @ImperioMP_Canal o -100123456789

class VideoEngine:
    @staticmethod
    def _telegram_worker(file_path):
        """Envía el archivo al canal de Telegram"""
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendVideo"
        try:
            with open(file_path, 'rb') as v:
                payload = {'chat_id': CHANNEL_ID, 'caption': f"🎬 Clip: {os.path.basename(file_path)}"}
                requests.post(url, data=payload, files={'video': v}, timeout=60)
                print(f"✅ Enviado a Telegram: {file_path}")
        except Exception as e:
            print(f"❌ Error subiendo a Telegram: {e}")

    @staticmethod
    def _ffmpeg_worker(input_file, start, duration, output):
        """Corta un segmento a hiper-velocidad"""
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-avoid_negative_ts', 'make_zero',
            output, '-y'
        ]
        subprocess.run(cmd, capture_output=True)
        return output

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        # 1. Obtener duración
        probe = [
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', input_file
        ]
        total_sec = float(subprocess.check_output(probe).decode().strip())

        # 2. Carpeta de salida
        folder_name = f"MALLY_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
        out_dir = os.path.join('media', 'exports', folder_name)
        os.makedirs(out_dir, exist_ok=True)

        # 3. Preparar lista de cortes
        tasks = []
        current = 0
        idx = 1
        while current < total_sec:
            out_path = os.path.join(out_dir, f"clip_{idx:03d}.mp4")
            tasks.append((input_file, current, segment_seconds, out_path))
            current += segment_seconds
            idx += 1

        # 4. EJECUCIÓN PARALELA NITRO
        print(f"⚡ Iniciando fragmentación de {len(tasks)} partes...")
        with ProcessPoolExecutor() as executor:
            # Cortamos todos los clips en paralelo
            generated_clips = list(executor.map(lambda p: VideoEngine._ffmpeg_worker(*p), tasks))

        # 5. SUBIDA AUTOMÁTICA (En orden)
        print("🚀 Subiendo clips al canal del Imperio...")
        for clip in generated_clips:
            VideoEngine._telegram_worker(clip)

        return out_dir
