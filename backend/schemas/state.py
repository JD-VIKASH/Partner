from pydantic import BaseModel
from typing import List, Dict, Any

class ContextResponse(BaseModel):
    profile: Dict[str, Any]
    goals: List[Dict[str, Any]]
    projects: List[Dict[str, Any]]
    skills: List[Dict[str, Any]]
