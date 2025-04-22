# app/graph_builder.py

from langgraph.graph import StateGraph
from app.state import MessageState
from app.nodes.listener_node import listener_node
from app.nodes.context_node import context_node
from app.nodes.llm_node import llm_node
from app.nodes.storage_node import storage_node

def build_graph():
    graph = StateGraph(MessageState)

    graph.add_node("Listener", listener_node)
    graph.add_node("Context", context_node)
    graph.add_node("LLM", llm_node)
    graph.add_node("Store", storage_node)

    graph.set_entry_point("Listener")
    graph.add_edge("Listener", "Context")
    graph.add_edge("Context", "LLM")
    graph.add_edge("LLM", "Store")
    graph.set_finish_point("Store")

    return graph.compile()
