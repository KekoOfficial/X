import json
import os

DB_PATH = "database/config.json"

class NexusDB:
    def __init__(self):
        os.makedirs("database", exist_ok=True)
        if not os.path.exists(DB_PATH):
            with open(DB_PATH, "w") as f:
                json.dump({"bot_token": "", "chat_id": ""}, f)

    def get_config(self):
        with open(DB_PATH, "r") as f:
            return json.load(f)

    def save_config(self, data):
        with open(DB_PATH, "w") as f:
            json.dump(data, f, indent=4)

db = NexusDB()
