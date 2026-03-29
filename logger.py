import time
import datetime

class Logger:
    def __init__(self, name="MallyCuts"):
        self.name = name

    def _time(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def info(self, msg):
        return self._format("INFO", msg)

    def success(self, msg):
        return self._format("SUCCESS", msg)

    def warning(self, msg):
        return self._format("WARNING", msg)

    def error(self, msg):
        return self._format("ERROR", msg)

    def ffmpeg(self, process_time, return_code, raw_log):
        clean = self._clean(raw_log)

        status = "SUCCESS" if return_code == 0 else "FAILED"

        return f"""
🎬 {self.name} FFmpeg LOG

📊 Estado: {status}
⏱ Tiempo: {process_time:.2f}s
🔁 Código: {return_code}
🕒 Hora: {self._time()}

📄 Detalles:
{clean if clean else "Sin detalles relevantes ⚡"}
"""

    def _format(self, level, msg):
        return f"[{self._time()}] [{level}] {msg}"

    def _clean(self, text):
        if not text:
            return ""

        lines = text.split("\n")
        important = []

        for line in lines:
            line = line.strip()

            if not line:
                continue

            keywords = [
                "error", "warning", "frame",
                "video", "audio", "time",
                "speed", "duration", "stream"
            ]

            if any(k in line.lower() for k in keywords):
                important.append(line)

        return "\n".join(important[-20:])