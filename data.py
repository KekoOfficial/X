import json
import os
from config import DB_PATH

class NexusDB:
    def __init__(self):
        self._cached_data = None
        if not os.path.exists(DB_PATH):
            self.save({"bot_token": "", "chat_id": ""})

    def get(self):
        if self._cached_data: return self._cached_data
        try:
            with open(DB_PATH, "r") as f:
                self._cached_data = json.load(f)
                return self._cached_data
        except:
            return {"bot_token": "", "chat_id": ""}

    def save(self, data):
        with open(DB_PATH, "w") as f:
            json.dump(data, f, indent=4)
        self._cached_data = data

db = NexusDB()
