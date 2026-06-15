import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import chat, state, memory, health, system, conversations, representative
import uvicorn

app = FastAPI(
    title="Frieren Cognitive Backend",
    description="One Brain, Many Devices - Centralized AI Logic",
    version="1.0.0"
)

# Enable CORS for PWA and client integrations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(chat.router)
app.include_router(state.router)
app.include_router(memory.router)
app.include_router(health.router)
app.include_router(system.router)
app.include_router(conversations.router)
app.include_router(representative.router)

if __name__ == "__main__":
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
