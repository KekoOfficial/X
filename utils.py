import os
import uuid
import subprocess
from config import DOWNLOAD_FOLDER, THUMB_FOLDER, CHAPTER_DURATION

def generate_unique_name(prefix="video"):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"

def cut_video_by_chapters(input_path, chapters=None):
    """
    Corta el vídeo en capítulos exactos (CHAPTER_DURATION).
    Si se especifica chapters, corta ese número de capítulos exactos.
    Devuelve lista de rutas de los vídeos cortados.
    """
    from moviepy.editor import VideoFileClip

    clip = VideoFileClip(input_path)
    duration = clip.duration
    output_files = []

    if chapters:
        duration_per_chapter = duration / chapters
    else:
        duration_per_chapter = CHAPTER_DURATION

    start = 0
    index = 1
    while start < duration:
        end = min(start + duration_per_chapter, duration)
        output_name = os.path.join(DOWNLOAD_FOLDER, f"chapter_{index}.mp4")
        subprocess.run([
            "ffmpeg", "-y", "-i", input_path,
            "-ss", str(start), "-to", str(end),
            "-c", "copy", output_name
        ])
        output_files.append(output_name)
        start = end
        index += 1

    return output_files