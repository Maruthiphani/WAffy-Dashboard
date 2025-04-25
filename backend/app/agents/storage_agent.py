# app/agents/storage_agent.py

import os
import json
from pathlib import Path
from datetime import datetime

class StorageAgent:
    def __init__(self, filepath="data/messages.json"):
        self.filepath = filepath
        Path(os.path.dirname(self.filepath)).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)

    def save_message(self, message_data: dict):
        try:
            with open(self.filepath, "r") as f:
                existing = json.load(f)
        except Exception:
            existing = []

        existing.append(message_data)

        try:
            with open(self.filepath, "w") as f:
                json.dump(existing, f, indent=2)
            print(f"[StorageAgent] Message saved for sender: {message_data.get('sender')}")
        except Exception as e:
            print(f"[StorageAgent] Error saving message:", e)

# ✅ Singleton for use in node
storage_agent = StorageAgent()
