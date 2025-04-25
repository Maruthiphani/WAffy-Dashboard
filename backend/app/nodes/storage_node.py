# app/nodes/storage_node.py

from app.agents.storage_agent import storage_agent
from app.state import MessageState
from pydantic import BaseModel

def storage_node(state: MessageState) -> MessageState:
    try:
        storage_agent.save_message(state.dict())
    except Exception as e:
        print("[StorageNode] Failed to save message:", e)
    return state
