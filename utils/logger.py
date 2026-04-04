import datetime

class Logger:
    def info(self, msg):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"[{now}] [INFO] {msg}")

log = Logger()
