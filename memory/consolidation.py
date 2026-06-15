import os
import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from memory.long_term_memory import LongTermMemory

class ConsolidatedTopic(BaseModel):
    topic_name: str = Field(description="A short name for the grouped topic.")
    consolidated_memory: str = Field(description="The summarized, high-quality consolidated memory combining multiple related facts.")
    redundant_memory_ids_to_delete: List[str] = Field(description="List of IDs of the original memories that have been merged and can now be deleted.")

class ConsolidationResult(BaseModel):
    topics: List[ConsolidatedTopic] = Field(description="List of consolidated topics derived from the raw memories.")

class MemoryConsolidator:
    def __init__(self, llm=None):
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = llm or ChatGroq(api_key=api_key, model="llama-3.1-8b-instant", temperature=0)
        self.structured_llm = self.llm.with_structured_output(ConsolidationResult)
        self.ltm = LongTermMemory()
        
        self.prompt = PromptTemplate.from_template(
            "You are a Memory Consolidation Expert for a Cognitive AI.\n"
            "Review the following list of raw memories (with their IDs).\n"
            "Your task:\n"
            "1. Group similar topics or related experiences.\n"
            "2. Summarize them into a single, compact, high-quality 'consolidated_memory'.\n"
            "3. Identify the original memory IDs that are now redundant and should be deleted.\n"
            "Ignore memories that don't need consolidation (leave them out of the output).\n\n"
            "Raw Memories:\n{memories}\n\n"
            "Consolidate and return the structured result."
        )

    def consolidate_collection(self, memory_type: str = "semantic"):
        """Runs the consolidation process for the specified collection."""
        print(f"🧹 [Starting Memory Consolidation for {memory_type} memory...]")
        
        if memory_type == "semantic":
            raw_memories = self.ltm.get_all_semantic_memories()
        else:
            raw_memories = self.ltm.get_all_episodic_memories()

        if not raw_memories or len(raw_memories) < 3:
            print("No need to consolidate (too few memories).")
            return

        # Format for LLM
        memories_str = "\n".join([f"ID: {m['id']} | Content: {m['document']}" for m in raw_memories])
        
        try:
            chain = self.prompt | self.structured_llm
            result = chain.invoke({"memories": memories_str})
            
            for topic in result.topics:
                if not topic.redundant_memory_ids_to_delete:
                    continue
                
                # Delete old
                if memory_type == "semantic":
                    self.ltm.delete_semantic_memories(topic.redundant_memory_ids_to_delete)
                else:
                    self.ltm.delete_episodic_memories(topic.redundant_memory_ids_to_delete)
                
                # Save new consolidated memory
                metadata = {
                    "category": "consolidated_" + memory_type,
                    "importance_score": 9.0,
                    "timestamp": datetime.now().isoformat(),
                    "topic": topic.topic_name
                }
                
                new_id = str(uuid.uuid4())
                if memory_type == "semantic":
                    self.ltm.save_semantic_memory(topic.consolidated_memory, metadata, new_id)
                else:
                    self.ltm.save_episodic_memory(topic.consolidated_memory, metadata, new_id)
                
                print(f"📦 [Consolidated Topic: '{topic.topic_name}'] -> Deleted {len(topic.redundant_memory_ids_to_delete)} redundant memories.")
                
        except Exception as e:
            print(f"[!] Consolidation Error: {e}")

    def run_full_consolidation(self):
        self.consolidate_collection("semantic")
        self.consolidate_collection("episodic")
