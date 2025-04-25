# app/nodes/listener_node.py

def listener_node(state: dict) -> dict:
    """
    Entry point of the LangGraph.
    This function receives the raw message state and passes it along.
    """
    print("[ListenerNode] Received message from:", state.sender)

    return state
