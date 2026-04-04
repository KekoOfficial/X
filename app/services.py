import subprocess
import os
import datetime
from concurrent.futures import ProcessPoolExecutor

class VideoEngine:
    @staticmethod
    def _ffmpeg_worker(input_file, start, duration, output):
        """Tarea individual para un núcleo de CPU"""
        cmd = [
            'ffmpeg', '-ss', str(start), '-t', str(duration),
            '-i', input_file, '-c', 'copy', '-avoid_negative_ts', 'make_zero',
            output, '-y'
        ]
        subprocess.run(cmd, capture_output=True)

    @staticmethod
    def execute_parallel_cut(input_file, segment_seconds=60):
        try:
            # 1. Obtener duración real con ffprobe
            duration_cmd = [
                'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1', input_file
            ]
            total_sec = float(subprocess.check_output(duration_cmd).decode().strip())

            # 2. Setup de carpetas
            folder_name = f"MALLY_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}"
            out_dir = os.path.join('media', 'exports', folder_name)
            os.makedirs(out_dir, exist_ok=True)

            # 3. Preparar lista de trabajos
            tasks = []
            current = 0
            idx = 1
            segment_seconds = int(segment_seconds)

            while current < total_sec:
                out_path = os.path.join(out_dir, f"clip_{idx:03d}.mp4")
                tasks.append((input_file, current, segment_seconds, out_path))
                current += segment_seconds
                idx += 1

            # 4. LANZAR MOTOR PARALELO (Nitro Mode)
            # Usa todos los núcleos disponibles para cortar 10 horas en segundos
            with ProcessPoolExecutor() as executor:
                executor.map(lambda p: VideoEngine._ffmpeg_worker(*p), tasks)

            return out_dir
        except Exception as e:
            print(f"❌ ERROR MOTOR V10: {e}")
            return None
