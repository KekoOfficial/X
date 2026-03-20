import os
import subprocess
import uuid
from config import DOWNLOAD_FOLDER

def generate_unique_name(prefix="video"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def cut_video_by_chapters(input_file, chapter_duration=15):
    # Obtener duración del vídeo
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", input_file],
        capture_output=True, text=True
    )
    total_duration = float(result.stdout.strip())
    num_chapters = int(total_duration // chapter_duration) + 1

    output_files = []
    for i in range(num_chapters):
        start = i * chapter_duration
        end = min((i + 1) * chapter_duration, total_duration)
        output_file = os.path.join(DOWNLOAD_FOLDER, f"chapter_{i+1}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", input_file,
            "-ss", str(start), "-to", str(end),
            "-c", "copy", output_file
        ])
        output_files.append(output_file)
    return output_files