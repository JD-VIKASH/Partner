import uuid
from typing import Dict
from datetime import datetime

class SessionManager:
    def __init__(self):
        # In-memory session store. For a production system, this would be in Redis.
        self.active_sessions: Dict[str, dict] = {}

    def get_or_create_session(self, user_id: str, device_id: str) -> str:
        """
        Retrieves an active session for the user/device pair, or creates a new one.
        Currently creating a unique session per device to allow concurrent sessions,
        but keeping the history linked to the user_id in WorkingMemory.
        """
        key = f"{user_id}:{device_id}"
        if key in self.active_sessions:
            self.active_sessions[key]["timestamp"] = datetime.now().isoformat()
            return self.active_sessions[key]["session_id"]
        
        new_session_id = str(uuid.uuid4())
        self.active_sessions[key] = {
            "user_id": user_id,
            "device_id": device_id,
            "session_id": new_session_id,
            "timestamp": datetime.now().isoformat()
        }
        return new_session_id

    def get_session_info(self, session_id: str) -> dict:
        for info in self.active_sessions.values():
            if info["session_id"] == session_id:
                return info
        return None
