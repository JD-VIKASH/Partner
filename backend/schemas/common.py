from pydantic import BaseModel
from typing import Optional

class BaseRequest(BaseModel):
    user_id: str
    device_id: Optional[str] = "unknown"
