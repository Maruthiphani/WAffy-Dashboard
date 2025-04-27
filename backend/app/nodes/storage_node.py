# app/nodes/storage_node.py

from app.agents.logger_agent import LoggerAgent
from app.state import MessageState
from pydantic import BaseModel

def storage_node(state: MessageState) -> MessageState:
    try:
        # Get user_id from business_phone_id if available
        business_phone_id = state.business_phone_id
        
        # Import the function directly
        from app.agents.logger_agent import get_user_id_from_business_phone_id
        user_id = get_user_id_from_business_phone_id(business_phone_id)
        
        if user_id:
            # Create logger agent with the found user_id
            logger_agent = LoggerAgent(str(user_id))
        else:
            # Fall back to user_id 4 if no user is found
            logger_agent = LoggerAgent("4")
            
        # Process the message using logger_agent
        logger_agent.process_messages([state.dict()])
    except Exception as e:
        print("[StorageNode] Failed to process message with logger_agent:", e)
    return state
