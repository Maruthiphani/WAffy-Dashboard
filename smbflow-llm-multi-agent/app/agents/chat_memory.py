from collections import defaultdict
from typing import List, Dict, Tuple
from datetime import datetime

class ChatMemoryManager:
    def __init__(self):
        self.memory: Dict[Tuple[str, str], List[Dict]] = defaultdict(list)

    def add_message(self, business_id: str, customer_id: str, sender_type: str, message: str):
        key = (business_id, customer_id)
        self.memory[key].append({
            "sender_type": sender_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_recent_messages(self, business_id: str, customer_id: str, limit: int = 10) -> List[Dict]:
        key = (business_id, customer_id)
        return self.memory[key][-limit:]

    def get_customer_messages(self, business_id: str, customer_id: str, limit: int = 10) -> List[str]:
        key = (business_id, customer_id)
        return [msg["message"] for msg in self.memory[key][-limit:] if msg["sender_type"] == "customer"]

    def clear_conversation(self, business_id: str, customer_id: str):
        key = (business_id, customer_id)
        self.memory[key] = []

# instantiate
chat_memory = ChatMemoryManager()
