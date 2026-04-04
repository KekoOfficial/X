import json
import os

DB_PATH = "database/config.json"

class NexusDB:
    def __init__(self):
        os.makedirs("database", exist_ok=True)
        if not os.path.exists(DB_PATH):
            self.save({"bot_token": "", "chat_id": ""})

    def get(self):
        try:
            with open(DB_PATH, "r") as f:
                return json.load(f)
        except:
            return {"bot_token": "", "chat_id": ""}

    def save(self, data):
        with open(DB_PATH, "w") as f:
            json.dump(data, f, indent=4)

db = NexusDB()
