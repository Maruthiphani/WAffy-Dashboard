from app.agents.context_agent import context_manager
from app.state import MessageState

def context_node(state: MessageState) -> MessageState:
    """
    Manages conversation context based on LLM's conversation_status:
    - "new" or "close" → clears context
    - "continue" → appends to ongoing context
    """
    if state.conversation_status in ["close", "new"]:
        print(f"[ContextNode] 🚪 Resetting context for {state.sender} (status: {state.conversation_status})")
        context_manager.clear_context(state.sender)
        state.context = []
    else:
        context = context_manager.get_context(state.sender)
        context_manager.add_message(state.sender, state.message)
        state.context = context

    print(f"[ContextNode] Context for {state.sender}: {state.context}")
    return state
