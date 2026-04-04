import subprocess
import os
from config.ffmpeg_config import FFMPEG_BINARY # Definido en tu carpeta config

def fast_segment_video(input_path, output_dir, segment_time=60):
    """
    Corta videos de hasta 10 horas en segundos.
    Usa -c copy para evitar renderizado y maximizar velocidad.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Patrón de salida ordenado: clip_001.mp4, clip_002.mp4...
    output_pattern = os.path.join(output_dir, "mally_clip_%03d.mp4")

    command = [
        'ffmpeg', '-i', input_path,
        '-c', 'copy', 
        '-map', '0',
        '-f', 'segment', 
        '-segment_time', str(segment_time),
        '-reset_timestamps', '1',
        output_pattern
    ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en el motor V10: {e.stderr}")
        return False
