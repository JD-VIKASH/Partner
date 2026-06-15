from pydantic import BaseModel
from backend.schemas.common import BaseRequest

class MemoryRequest(BaseRequest):
    content: str
    category: str # 'event', 'preference', etc.
    importance_score: float = 7.0

class ConsolidateRequest(BaseRequest):
    memory_type: str = "semantic" # 'semantic' or 'episodic'
