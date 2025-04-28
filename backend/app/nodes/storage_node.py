# app/nodes/storage_node.py

from app.agents.logger_agent import LoggerAgent
from app.state import MessageState
from pydantic import BaseModel

def storage_node(state: MessageState) -> MessageState:
    try:
        business_phone_id = state.business_phone_id
        
        from app.agents.logger_agent import get_user_id_from_business_phone_id
        user_id = get_user_id_from_business_phone_id(business_phone_id)
        
        if user_id:
            logger_agent = LoggerAgent(str(user_id))
        else:
            logger_agent = LoggerAgent("4")
            
        logger_agent.process_messages([state.dict()])
    except Exception as e:
        print("[StorageNode] Failed to save message:", e)
    return state
