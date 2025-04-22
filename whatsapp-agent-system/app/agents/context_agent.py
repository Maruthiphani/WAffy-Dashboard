from collections import defaultdict, deque
from datetime import datetime, timedelta

class ContextManager:
    def __init__(self, max_history=5, expiry_minutes=30):
        self.history = defaultdict(lambda: deque(maxlen=max_history))
        self.expiry = timedelta(minutes=expiry_minutes)

    def add_message(self, sender, message):
        now = datetime.utcnow()
        self.history[sender].append({"message": message, "timestamp": now})

    def get_context(self, sender):
        now = datetime.utcnow()
        return [
            entry["message"]
            for entry in self.history[sender]
            if now - entry["timestamp"] <= self.expiry
        ]

context_manager = ContextManager()
