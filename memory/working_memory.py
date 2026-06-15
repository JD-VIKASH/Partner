import os
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import BaseMessage

class WorkingMemory:
    def __init__(self, session_id: str = "default_session"):
        self.session_id = session_id
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.history = self._init_history()

    def _init_history(self):
        try:
            from langchain_community.chat_message_histories import RedisChatMessageHistory
            history = RedisChatMessageHistory(session_id=self.session_id, url=self.redis_url)
            # Eagerly test the connection so we fail fast to the fallback
            _ = history.messages
            return history
        except Exception as e:
            print(f"[!] Warning: Redis not available. Falling back to in-memory history. ({e})")
            return ChatMessageHistory()
            
    def get_messages(self) -> list[BaseMessage]:
        return self.history.messages
        
    def add_message(self, message: BaseMessage):
        self.history.add_message(message)

    def add_messages(self, messages: list[BaseMessage]):
        self.history.add_messages(messages)
        
    def clear(self):
        self.history.clear()
