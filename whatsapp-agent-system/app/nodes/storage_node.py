from app.agents.storage_agent import storage_agent

def storage_node(state) -> dict:
    """
    Final node in LangGraph: saves the processed message to JSON.
    """
    message_dict = state.dict()

    storage_agent.save(message_dict)

    return state
