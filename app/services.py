import subprocess
import os
import datetime
from concurrent.futures import ProcessPoolExecutor

class VideoEngine:
    @staticmethod
    def _execute_single_cut(input_file, start_time, duration, output_path):
        """Función interna para ejecutar un solo corte a máxima velocidad"""
        command = [
            'ffmpeg', '-ss', str(start_time), 
            '-t', str(duration),
            '-i', input_file,
            '-c', 'copy', # Stream Copy: No renderiza, solo copia bits
            '-avoid_negative_ts', 'make_zero',
            output_path, '-y'
        ]
        subprocess.run(command, capture_output=True)

    @staticmethod
    def execute_fast_cut(input_file, segment_seconds=60):
        # 1. Obtener duración total del video (rápido)
        probe = subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1', input_file
        ]).decode('utf-8').strip()
        
        total_duration = float(probe)
        
        # 2. Preparar carpeta de salida
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        out_dir = os.path.join('media/exports', f"MALLY_PARALLEL_{timestamp}")
        os.makedirs(out_dir, exist_ok=True)

        # 3. Crear lista de tareas (Cortes)
        tasks = []
        current_start = 0
        clip_index = 1
        
        while current_start < total_duration:
            output_name = os.path.join(out_dir, f"clip_{clip_index:03d}.mp4")
            tasks.append((input_file, current_start, segment_seconds, output_name))
            current_start += segment_seconds
            clip_index += 1

        # 4. LANZAR MOTOR MULTI-NÚCLEO (Paralelismo Real)
        # Usa ProcessPoolExecutor para aprovechar todos los núcleos de tu CPU
        with ProcessPoolExecutor() as executor:
            executor.map(lambda p: VideoEngine._execute_single_cut(*p), tasks)

        return out_dir
