import asyncio
from memory.memory_filter import MemoryFilter
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
import os

class ReflectionSystem:
    def __init__(self):
        self.memory_filter = MemoryFilter()
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = ChatGroq(api_key=api_key, model="llama-3.1-8b-instant", temperature=0.5)
        
        self.reflection_prompt = PromptTemplate.from_template(
            "Reflect on the following conversation exchange. "
            "Identify any implicit user needs, emotional state, or subtext.\n\n"
            "User: {user_input}\n"
            "Frieren: {ai_response}\n\n"
            "Reflection:"
        )

    async def run_reflection_cycle(self, user_input: str, ai_response: str):
        """
        Executes the Reflection Validation Layer workflow:
        Reflection -> Memory Filter -> Memory Storage
        """
        try:
            # 1. Reflection
            reflection_chain = self.reflection_prompt | self.llm
            reflection_result = await reflection_chain.ainvoke({"user_input": user_input, "ai_response": ai_response})
            reflection_text = reflection_result.content
            print(f"🪞 [Reflection]: {reflection_text}")
            
            # 2. Memory Filter -> 3. Memory Storage (Handled internally by MemoryFilter)
            # We pass both the raw exchange and the reflection to be filtered.
            combined_context = f"Exchange: User: {user_input} | Frieren: {ai_response}\nReflection: {reflection_text}"
            
            # Run memory filtering synchronously in an executor if it doesn't support async directly
            # For simplicity, calling the sync method here (should be fine for a background thread/task)
            self.memory_filter.process_and_store(user_input, combined_context)
            
        except Exception as e:
            print(f"[!] Reflection System Error: {e}")

    def trigger_reflection(self, user_input: str, ai_response: str):
        """Fire and forget reflection task."""
        asyncio.create_task(self.run_reflection_cycle(user_input, ai_response))
