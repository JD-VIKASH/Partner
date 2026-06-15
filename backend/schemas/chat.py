from pydantic import BaseModel
from backend.schemas.common import BaseRequest

class ChatRequest(BaseRequest):
    message: str

class ChatResponse(BaseModel):
    response: str
    session_id: str

class ReflectionRequest(BaseRequest):
    user_input: str
    ai_response: str
