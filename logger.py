import datetime

class Logger:
    def __init__(self):
        self.log_file = "database/system.log"

    def _write(self, level, msg):
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{now}] [{level}] {msg}\n"
        print(entry, end="")
        with open(self.log_file, "a") as f:
            f.write(entry)

    def info(self, msg): self._write("INFO", msg)
    def error(self, msg): self._write("ERROR", msg)
