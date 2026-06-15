from backend.services.context_builder import ContextBuilderService
from backend.services.session_manager import SessionManager
from backend.services.user_identity import UserIdentityService
from core.reasoning import ReasoningEngine
from core.reflection import ReflectionSystem
from memory.working_memory import WorkingMemory

class OrchestrationService:
    def __init__(self):
        self.context_builder = ContextBuilderService()
        self.session_manager = SessionManager()
        self.user_identity = UserIdentityService()
        self.reasoning_engine = ReasoningEngine()
        self.reflection = ReflectionSystem()
        
        # Route the ReasoningEngine's context assembler to the central ContextBuilderService
        self.reasoning_engine._assemble_context = self.context_builder.assemble_context_string

    def process_chat(self, user_id: str, device_id: str, message: str) -> dict:
        self.user_identity.validate_user(user_id)
        session_id = self.session_manager.get_or_create_session(user_id, device_id)
        
        # Use session-specific working memory so devices stay isolated in conversation history
        self.reasoning_engine.working_memory = WorkingMemory(session_id=session_id)
        
        # generate_response handles context assembly, tool calls, memory updates and reflection
        output = self.reasoning_engine.generate_response(message)
        
        return {
            "response": output,
            "session_id": session_id
        }

    def process_reflection(self, user_input: str, ai_response: str):
        self.reflection.trigger_reflection(user_input, ai_response)
        
    def get_context(self) -> dict:
        return self.context_builder.get_raw_state()
