from fastapi import APIRouter, Depends
from backend.schemas.chat import ChatRequest, ChatResponse, ReflectionRequest
from backend.services.orchestration import OrchestrationService
from backend.auth.security import get_api_key
from db.database import get_connection
from datetime import datetime

router = APIRouter(prefix="/api/v1", dependencies=[Depends(get_api_key)])
orchestrator = OrchestrationService()

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    result = orchestrator.process_chat(request.user_id, request.device_id, request.message)
    
    # Log conversation to SQLite for PWA Control Center history
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Conversations (user_id, device_id, session_id, user_message, ai_response, timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (request.user_id, request.device_id, result["session_id"], request.message, result["response"], datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[!] Warning: Failed to log conversation to SQLite: {e}")
        
    return ChatResponse(response=result["response"], session_id=result["session_id"])


@router.post("/reflection")
async def reflection_endpoint(request: ReflectionRequest):
    orchestrator.process_reflection(request.user_input, request.ai_response)
    return {"status": "Reflection triggered in background."}
