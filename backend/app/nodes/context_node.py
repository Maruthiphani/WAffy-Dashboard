from app.state import MessageState
from app.agents.chat_memory import chat_memory

def context_node(state: MessageState) -> MessageState:
    """
    Handles context per (business_id, customer_id), storing full conversation:
    - Adds current message to memory
    - Extracts recent customer-only messages for context
    - Clears memory if conversation is "new" or "close"
    """
    biz_id = state.business_phone_number
    cust_id = state.customer_id

    # Reset if convo is over or restarted
    if state.conversation_status in ["new", "close"]:
        print(f"[ContextNode] Resetting chat memory for ({biz_id}, {cust_id})")
        chat_memory.clear_conversation(biz_id, cust_id)
        state.context = []
    else:
        # Store current message as 'customer'
        chat_memory.add_message(biz_id, cust_id, sender_type="customer", message=state.message)

        # Retrieve last 10 customer messages
        customer_context = chat_memory.get_customer_messages(biz_id, cust_id, limit=10)
        state.context = customer_context

    print(f"[ContextNode] Final context for {cust_id}: {state.context}")
    return state
