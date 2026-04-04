import subprocess
import os
import datetime

class VideoEngine:
    @staticmethod
    def execute_fast_cut(input_file, seconds=60):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        out_dir = os.path.join('media/exports', f"MALLY_{timestamp}")
        os.makedirs(out_dir, exist_ok=True)
        
        # -c copy: La clave para la velocidad absoluta (Stream Copy)
        command = [
            'ffmpeg', '-i', input_file,
            '-c', 'copy', '-f', 'segment',
            '-segment_time', str(seconds),
            '-reset_timestamps', '1',
            os.path.join(out_dir, "clip_%03d.mp4")
        ]
        
        try:
            subprocess.run(command, check=True)
            return out_dir
        except Exception as e:
            print(f"Error Crítico: {e}")
            return None
