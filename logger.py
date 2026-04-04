import datetime

class Logger:
    def __init__(self):
        self.log_file = "database/system.log"

    def _log(self, level, msg):
        time_str = datetime.datetime.now().strftime("%H:%M:%S")
        entry = f"[{time_str}] [{level}] {msg}"
        print(entry)
        with open(self.log_file, "a") as f:
            f.write(entry + "\n")

    def info(self, msg): self._log("INFO", msg)
    def error(self, msg): self._log("ERROR", msg)

log = Logger()
