import os
import uuid
from moviepy.editor import VideoFileClip
from config import DOWNLOAD_FOLDER, CHAPTER_DURATION

def generate_unique_name(original_name):
    ext = os.path.splitext(original_name)[1]
    return f"{uuid.uuid4().hex}{ext}"

def cut_video_by_chapters(file_path, chapters=None, chapter_duration=CHAPTER_DURATION):
    video = VideoFileClip(file_path)
    total_duration = int(video.duration)
    
    # Si no se indica cantidad de capítulos, calcular automático
    if chapters:
        chapter_duration = max(1, total_duration // chapters)
    else:
        chapters = total_duration // chapter_duration + (1 if total_duration % chapter_duration else 0)

    output_files = []
    start = 0
    for i in range(1, chapters+1):
        end = min(start + chapter_duration, total_duration)
        output_name = f"video#{i}{os.path.splitext(file_path)[1]}"
        output_path = os.path.join(DOWNLOAD_FOLDER, output_name)
        video.subclip(start, end).write_videofile(output_path, codec="libx264", audio_codec="aac", verbose=False, logger=None)
        output_files.append(output_name)
        start += chapter_duration
    return output_files