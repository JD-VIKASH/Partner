import os
import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_core.embeddings import Embeddings

# We need an embedding model. Since Groq doesn't provide embeddings out of the box in the same way,
# we might use HuggingFace embeddings or let Chroma use its default sentence-transformers model.
# Using default Chroma embeddings for simplicity and zero-config local runs.

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'chroma_data')

class LongTermMemory:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=DB_PATH)
        # Using default embeddings from chromadb
        self.episodic_collection = self.client.get_or_create_collection(name="episodic_memory")
        self.semantic_collection = self.client.get_or_create_collection(name="semantic_memory")
    
    def save_episodic_memory(self, content: str, metadata: dict, memory_id: str):
        """Store an event, conversation, or time-sensitive experience."""
        self.episodic_collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )

    def save_semantic_memory(self, content: str, metadata: dict, memory_id: str):
        """Store identity, preferences, skills, or persistent facts."""
        self.semantic_collection.upsert(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
    
    def retrieve_episodic(self, query: str, n_results: int = 3):
        """Retrieve recent or relevant experiences."""
        if self.episodic_collection.count() == 0:
            return []
            
        results = self.episodic_collection.query(
            query_texts=[query],
            n_results=min(n_results, self.episodic_collection.count())
        )
        
        memories = []
        if results['documents']:
            for docs in results['documents']:
                memories.extend(docs)
        return memories

    def retrieve_semantic(self, query: str, n_results: int = 3):
        """Retrieve persistent knowledge or identity."""
        if self.semantic_collection.count() == 0:
            return []
            
        results = self.semantic_collection.query(
            query_texts=[query],
            n_results=min(n_results, self.semantic_collection.count())
        )
        
        memories = []
        if results['documents']:
            for docs in results['documents']:
                memories.extend(docs)
        return memories

    def get_all_semantic_memories(self):
        """Retrieve all semantic memories with their IDs for consolidation."""
        if self.semantic_collection.count() == 0:
            return []
        # Get all records
        data = self.semantic_collection.get()
        memories = []
        for i in range(len(data['ids'])):
            memories.append({
                "id": data['ids'][i],
                "document": data['documents'][i],
                "metadata": data['metadatas'][i]
            })
        return memories

    def delete_semantic_memories(self, ids: list[str]):
        """Delete specific semantic memories by ID."""
        if ids:
            self.semantic_collection.delete(ids=ids)

    def get_all_episodic_memories(self):
        """Retrieve all episodic memories with their IDs for consolidation."""
        if self.episodic_collection.count() == 0:
            return []
        data = self.episodic_collection.get()
        memories = []
        for i in range(len(data['ids'])):
            memories.append({
                "id": data['ids'][i],
                "document": data['documents'][i],
                "metadata": data['metadatas'][i]
            })
        return memories

    def delete_episodic_memories(self, ids: list[str]):
        """Delete specific episodic memories by ID."""
        if ids:
            self.episodic_collection.delete(ids=ids)
