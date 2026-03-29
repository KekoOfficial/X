import datetime
import time

class Logger:
    def __init__(self, name="MallyCuts"):
        self.name = name

    def _time(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # =========================
    # 📌 BASIC LOGS
    # =========================
    def info(self, msg):
        return self._format("INFO", msg)

    def success(self, msg):
        return self._format("SUCCESS", msg)

    def warning(self, msg):
        return self._format("WARNING", msg)

    def error(self, msg):
        return self._format("ERROR", msg)

    # =========================
    # 🎬 FFMPEG LOG CLEAN
    # =========================
    def ffmpeg(self, process_time, return_code, raw):
        clean = self._clean(raw)
        status = "SUCCESS" if return_code == 0 else "FAILED"

        return f"""
🎬 {self.name} ENGINE LOG

📊 Status: {status}
⏱ Time: {round(process_time,2)}s
🔁 Code: {return_code}
🕒 Time: {self._time()}

📄 OUTPUT:
{clean if clean else "No relevant output ⚡"}
"""

    # =========================
    # 🔧 INTERNAL FORMAT
    # =========================
    def _format(self, level, msg):
        return f"[{self._time()}] [{level}] {msg}"

    # =========================
    # 🧹 CLEAN FFMPEG OUTPUT
    # =========================
    def _clean(self, text):
        if not text:
            return ""

        lines = text.split("\n")
        out = []

        keys = ["error", "warning", "frame", "fps", "speed", "video", "audio", "stream"]

        for l in lines:
            l = l.strip()
            if any(k in l.lower() for k in keys):
                out.append(l)

        return "\n".join(out[-20:])