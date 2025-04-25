# app/main.py

from fastapi import FastAPI
from dotenv import load_dotenv
from app.graph_builder import build_graph
from app.agents.listener_agent import get_listener_router

load_dotenv()

graph = build_graph()
app = FastAPI()
app.include_router(get_listener_router(graph))
