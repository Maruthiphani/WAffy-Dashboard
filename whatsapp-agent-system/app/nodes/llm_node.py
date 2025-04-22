# app/nodes/llm_node.py

from app.agents.llm_agent import GeminiLLMAgent

# Initialize the Gemini LLM agent (single instance)
llm_agent = GeminiLLMAgent()

def llm_node(state: dict) -> dict:
    """
    Uses Gemini to:
    - Classify message
    - Assign priority
    - Extract structured info
    - Determine conversation status
    Then updates the state with this data.
    """
    message = state.message
    context = state.context or []

    if not message:
        print("[LLMNode] No message to analyze")
        return state

    result = llm_agent.analyze(message, context)

    state.predicted_category = result.get("category", "unknown")
    state.priority = result.get("priority", "moderate")
    state.extracted_info = result.get("extracted_info", {})
    state.conversation_status = result.get("conversation_status", "continue")

    print(f"[LLMNode] Analysis result: {result}")
    return state
