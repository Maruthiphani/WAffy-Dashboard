# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
from app.graph_builder import build_graph
from app.agents.listener_agent import get_listener_router

# Load environment variables from .env file
load_dotenv()

graph = build_graph()

# Initialize the FastAPI application
app = FastAPI()

# Register the listener agent routes (for webhook verification and message handling)
app.include_router(get_listener_router(graph))
