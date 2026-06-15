import os
from typing import List
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

class EvaluatedMemory(BaseModel):
    memory: str = Field(description="The exact text of the memory being evaluated.")
    relevance: float = Field(description="Score between 0.0 and 1.0 indicating how relevant this memory is to the user's query.")
    confidence: float = Field(description="Score between 0.0 and 1.0 indicating how confident the system is that this memory is factual, not outdated, and useful.")

class MemoryEvaluationList(BaseModel):
    evaluations: List[EvaluatedMemory] = Field(description="List of evaluated memories.")

class RetrievalEvaluator:
    def __init__(self, llm=None):
        api_key = os.getenv("GROQ_API_KEY")
        self.llm = llm or ChatGroq(api_key=api_key, model="llama-3.1-8b-instant", temperature=0)
        self.structured_llm = self.llm.with_structured_output(MemoryEvaluationList)
        
        self.evaluation_prompt = PromptTemplate.from_template(
            "You are a strict Retrieval Evaluation Layer for a Cognitive AI.\n"
            "Your task is to evaluate a list of retrieved memories against the user's current query.\n\n"
            "Criteria:\n"
            "1. Semantic Relevance (relevance): Does this memory actually help answer or provide context for the query?\n"
            "2. Confidence (confidence): Is this memory a distinct, high-quality fact? (Penalize duplicates, noisy/vague memories, or likely outdated context).\n\n"
            "User Query: {user_query}\n\n"
            "Retrieved Memories:\n{memories}\n\n"
            "Evaluate each memory and return the structured list."
        )

    def evaluate(self, user_query: str, retrieved_memories: List[str]) -> List[dict]:
        """
        Evaluates raw memories, filters out low quality/irrelevant ones, 
        and returns the highest quality memories ranked.
        """
        if not retrieved_memories:
            return []

        # Format memories for the prompt
        memories_str = "\n".join([f"- {m}" for m in retrieved_memories])
        
        try:
            chain = self.evaluation_prompt | self.structured_llm
            result = chain.invoke({"user_query": user_query, "memories": memories_str})
            
            # Filter and rank
            valid_memories = []
            for eval_item in result.evaluations:
                # Reject if relevance or confidence is too low
                if eval_item.relevance >= 0.6 and eval_item.confidence >= 0.7:
                    valid_memories.append({
                        "memory": eval_item.memory,
                        "relevance": eval_item.relevance,
                        "confidence": eval_item.confidence
                    })
            
            # Sort by a combined score of relevance and confidence descending
            valid_memories.sort(key=lambda x: x['relevance'] + x['confidence'], reverse=True)
            
            return valid_memories
            
        except Exception as e:
            print(f"[!] Retrieval Evaluator Error: {e}")
            # Fallback: if LLM fails, just return everything to avoid breaking the pipeline, 
            # but assign default dummy scores.
            return [{"memory": m, "relevance": 1.0, "confidence": 1.0} for m in retrieved_memories]
