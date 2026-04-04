# logger.py
from datetime import datetime

class Logger:
    def info(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] ⚡ {msg}")

    def success(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] 🔥 {msg}")

    def error(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] ❌ {msg}")
