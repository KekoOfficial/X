import datetime

class Logger:
    def info(self, msg): self._log("INFO", msg)
    def success(self, msg): self._log("OK", msg)
    def error(self, msg): self._log("ERR", msg)

    def _log(self, level, msg):
        t = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{t}] [{level}] {msg}")

    def ffmpeg_report(self, job_id, duration):
        print(f"\n🎬 ENGINE REPORT | Job: {job_id}")
        print(f"⏱ Tiempo de proceso: {round(duration, 2)}s")
        print("-" * 30)
