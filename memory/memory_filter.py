from pydantic import BaseModel, Field
from typing import List, Optional
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from memory.long_term_memory import LongTermMemory
import os

class MemoryFact(BaseModel):
    category: str = Field(description="Category of the memory: 'event', 'conversation' (episodic) or 'preference', 'fact', 'identity', 'skill' (semantic)")
    fact: str = Field(description="The actual memory content to store")
    importance_score: float = Field(description="Score from 1 to 10 on how important this is to remember long-term")

class MemoryExtraction(BaseModel):
    facts: List[MemoryFact] = Field(description="List of extracted facts from the conversation")

class MemoryFilter:
    def __init__(self, llm=None):
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = llm or ChatGroq(api_key=api_key, model="llama-3.1-8b-instant", temperature=0)
        self.structured_llm = self.llm.with_structured_output(MemoryExtraction)
        self.ltm = LongTermMemory()
        
        self.prompt = PromptTemplate.from_template(
            "Analyze the following conversation snippet and extract any important long-term facts, "
            "user preferences, project details, or significant events.\n"
            "Do NOT extract temporary noise, greetings, or short-term context.\n"
            "If nothing is worth remembering, return an empty list.\n\n"
            "User said: {user_input}\n"
            "AI responded: {ai_response}\n\n"
            "Extract facts:"
        )

    def process_and_store(self, user_input: str, ai_response: str):
        """Extract facts and store them in Long-Term Memory if they pass the threshold."""
        try:
            chain = self.prompt | self.structured_llm
            result = chain.invoke({"user_input": user_input, "ai_response": ai_response})
            
            import uuid
            from datetime import datetime
            
            for fact in result.facts:
                if fact.importance_score >= 5.0:  # Threshold for useful information
                    metadata = {
                        "category": fact.category,
                        "importance_score": fact.importance_score,
                        "timestamp": datetime.now().isoformat()
                    }
                    
                    memory_id = str(uuid.uuid4())
                    if fact.category in ['event', 'conversation']:
                        self.ltm.save_episodic_memory(content=fact.fact, metadata=metadata, memory_id=memory_id)
                        collection_type = "Episodic"
                    else:
                        self.ltm.save_semantic_memory(content=fact.fact, metadata=metadata, memory_id=memory_id)
                        collection_type = "Semantic"
                        
                    print(f"💾 [{collection_type} Memory Stored: {fact.fact} (Score: {fact.importance_score})]")
        except Exception as e:
            print(f"[!] Memory Filter Error: {e}")
