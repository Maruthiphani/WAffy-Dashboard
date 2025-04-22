import os
import json
from pathlib import Path

class StorageAgent:
    def __init__(self, filepath="data/messages.json"):
        self.filepath = filepath

        # Ensure the data directory exists
        Path(os.path.dirname(self.filepath)).mkdir(parents=True, exist_ok=True)

        # Initialize file if missing
        if not os.path.exists(self.filepath):
            with open(self.filepath, "w") as f:
                json.dump([], f)

    def save(self, message: dict):
        try:
            # Read existing messages
            with open(self.filepath, "r") as f:
                try:
                    data = json.load(f)
                    if not isinstance(data, list):
                        raise ValueError("Storage file must contain a list")
                except json.JSONDecodeError:
                    data = []

            # Append the new message
            data.append(message)

            # Save updated data
            with open(self.filepath, "w") as f:
                json.dump(data, f, indent=2)

            print(f"[StorageAgent] ✅ Message saved for sender: {message.get('sender')}")

        except Exception as e:
            print(f"[StorageAgent] ❌ Error saving message: {e}")

# Export singleton for import in nodes
storage_agent = StorageAgent()
