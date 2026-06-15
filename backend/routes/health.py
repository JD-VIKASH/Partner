from fastapi import APIRouter
import redis
import sqlite3
import chromadb
from db.database import DB_PATH
import os
import json

router = APIRouter(prefix="/api/v1")

@router.get("/health")
async def health_check():
    status = {
        "status": "healthy",
        "redis": "disconnected",
        "chromadb": "disconnected",
        "sqlite": "disconnected",
        "memory_system": "degraded",
        "reasoning_engine": "inactive",
        "reflection_engine": "inactive",
        "representative_engine": "active",
        "proactive_assistant": "active"
    }
    
    # Check SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.cursor().execute("SELECT 1")
        conn.close()
        status["sqlite"] = "connected"
    except Exception:
        pass
        
    # Check Redis
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=1.0)
        r.ping()
        status["redis"] = "connected"
    except Exception:
        pass
        
    # Check Chroma
    try:
        chroma_path = os.path.join(os.path.dirname(DB_PATH), 'chroma_data')
        chromadb.PersistentClient(path=chroma_path)
        status["chromadb"] = "connected"
    except Exception:
        pass

    # Memory System status
    if status["sqlite"] == "connected" and status["chromadb"] == "connected":
        status["memory_system"] = "active"

    # Reasoning and Reflection Engine status
    if os.getenv("GROQ_API_KEY"):
        status["reasoning_engine"] = "active"
        status["reflection_engine"] = "active"

    # Proactive Assistant status based on Sleep/Wake state
    status_file = os.path.join(os.path.dirname(DB_PATH), 'system_status.json')
    try:
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                state_data = json.load(f)
                if state_data.get("state") == "SLEEPING":
                    status["proactive_assistant"] = "paused"
    except Exception:
        pass

    return status

