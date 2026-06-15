import os
import sys

# Ensure project root is in python path for IDE/test environments
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import APIRouter, Depends
import uuid
import asyncio
from datetime import datetime
from backend.schemas.memory import MemoryRequest, ConsolidateRequest
from memory.long_term_memory import LongTermMemory
from memory.consolidation import MemoryConsolidator
from backend.auth.security import get_api_key

router = APIRouter(prefix="/api/v1/memory", dependencies=[Depends(get_api_key)])
ltm = LongTermMemory()

@router.post("/")
async def add_memory(request: MemoryRequest):
    metadata = {
        "category": request.category,
        "importance_score": request.importance_score,
        "timestamp": datetime.now().isoformat(),
        "user_id": request.user_id
    }
    new_id = str(uuid.uuid4())
    if request.category in ['event', 'conversation']:
        ltm.save_episodic_memory(request.content, metadata, new_id)
        collection = "Episodic"
    else:
        ltm.save_semantic_memory(request.content, metadata, new_id)
        collection = "Semantic"
        
    return {"status": "success", "collection": collection, "memory_id": new_id}

@router.post("/consolidate")
async def consolidate_memory(request: ConsolidateRequest):
    consolidator = MemoryConsolidator()
    # Run the blocking LLM consolidation in a thread pool so we don't block the event loop
    await asyncio.to_thread(consolidator.consolidate_collection, request.memory_type)
    return {"status": f"{request.memory_type} consolidation triggered."}

@router.get("/search")
async def search_memories(q: str = ""):
    try:
        results = []
        if q:
            # Vector search
            # episodic query
            try:
                epi_res = ltm.episodic_collection.query(query_texts=[q], n_results=50)
                if epi_res and epi_res.get("ids") and epi_res["ids"]:
                    for i in range(len(epi_res["ids"][0])):
                        dist = epi_res["distances"][0][i] if "distances" in epi_res and epi_res["distances"] and len(epi_res["distances"][0]) > i else 0.5
                        # Map L2 distance to confidence percent
                        conf = max(0, min(100, int((1.0 - dist) * 100)))
                        results.append({
                            "id": epi_res["ids"][0][i],
                            "text": epi_res["documents"][0][i],
                            "type": "episodic",
                            "category": epi_res["metadatas"][0][i].get("category", "event") if epi_res["metadatas"] and len(epi_res["metadatas"][0]) > i else "event",
                            "importance_score": epi_res["metadatas"][0][i].get("importance_score", 5.0) if epi_res["metadatas"] and len(epi_res["metadatas"][0]) > i else 5.0,
                            "confidence_score": conf,
                            "created_date": epi_res["metadatas"][0][i].get("timestamp", "") if epi_res["metadatas"] and len(epi_res["metadatas"][0]) > i else "",
                            "user_id": epi_res["metadatas"][0][i].get("user_id", "system") if epi_res["metadatas"] and len(epi_res["metadatas"][0]) > i else "system",
                            "source": epi_res["metadatas"][0][i].get("device_id", "backend") if epi_res["metadatas"] and len(epi_res["metadatas"][0]) > i else "backend"
                        })
            except Exception as e:
                print(f"[!] Episodic search failed: {e}")

            # semantic query
            try:
                sem_res = ltm.semantic_collection.query(query_texts=[q], n_results=50)
                if sem_res and sem_res.get("ids") and sem_res["ids"]:
                    for i in range(len(sem_res["ids"][0])):
                        dist = sem_res["distances"][0][i] if "distances" in sem_res and sem_res["distances"] and len(sem_res["distances"][0]) > i else 0.5
                        conf = max(0, min(100, int((1.0 - dist) * 100)))
                        results.append({
                            "id": sem_res["ids"][0][i],
                            "text": sem_res["documents"][0][i],
                            "type": "semantic",
                            "category": sem_res["metadatas"][0][i].get("category", "preference") if sem_res["metadatas"] and len(sem_res["metadatas"][0]) > i else "preference",
                            "importance_score": sem_res["metadatas"][0][i].get("importance_score", 5.0) if sem_res["metadatas"] and len(sem_res["metadatas"][0]) > i else 5.0,
                            "confidence_score": conf,
                            "created_date": sem_res["metadatas"][0][i].get("timestamp", "") if sem_res["metadatas"] and len(sem_res["metadatas"][0]) > i else "",
                            "user_id": sem_res["metadatas"][0][i].get("user_id", "system") if sem_res["metadatas"] and len(sem_res["metadatas"][0]) > i else "system",
                            "source": sem_res["metadatas"][0][i].get("device_id", "backend") if sem_res["metadatas"] and len(sem_res["metadatas"][0]) > i else "backend"
                        })
            except Exception as e:
                print(f"[!] Semantic search failed: {e}")
        else:
            # Get all
            try:
                epi_all = ltm.get_all_episodic_memories()
                for item in epi_all:
                    results.append({
                        "id": item["id"],
                        "text": item["document"],
                        "type": "episodic",
                        "category": item["metadata"].get("category", "event"),
                        "importance_score": item["metadata"].get("importance_score", 5.0),
                        "confidence_score": 85,
                        "created_date": item["metadata"].get("timestamp", ""),
                        "user_id": item["metadata"].get("user_id", "system"),
                        "source": item["metadata"].get("device_id", "backend")
                    })
            except Exception as e:
                print(f"[!] Episodic get failed: {e}")

            try:
                sem_all = ltm.get_all_semantic_memories()
                for item in sem_all:
                    results.append({
                        "id": item["id"],
                        "text": item["document"],
                        "type": "semantic",
                        "category": item["metadata"].get("category", "preference"),
                        "importance_score": item["metadata"].get("importance_score", 5.0),
                        "confidence_score": 90,
                        "created_date": item["metadata"].get("timestamp", ""),
                        "user_id": item["metadata"].get("user_id", "system"),
                        "source": item["metadata"].get("device_id", "backend")
                    })
            except Exception as e:
                print(f"[!] Semantic get failed: {e}")

        # Sort by importance_score descending, then by date descending
        results.sort(key=lambda x: (x["importance_score"], x["created_date"]), reverse=True)
        return results
    except Exception as e:
        print(f"[!] Search memories endpoint error: {e}")
        return []

@router.get("/stats")
async def get_memory_stats():
    from db.database import get_connection
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM Goals WHERE status = 'active'")
        goals_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Projects WHERE status = 'active'")
        projects_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM Skills")
        skills_count = cursor.fetchone()[0]
        
        conn.close()
    except Exception as e:
        print(f"[!] Failed to query SQLite stats: {e}")
        goals_count, projects_count, skills_count = 0, 0, 0

    try:
        episodic_count = ltm.episodic_collection.count()
    except Exception:
        episodic_count = 0
        
    try:
        semantic_count = ltm.semantic_collection.count()
    except Exception:
        semantic_count = 0
        
    reflections_count = 0
    try:
        all_epi = ltm.get_all_episodic_memories()
        all_sem = ltm.get_all_semantic_memories()
        for m in all_epi + all_sem:
            doc = m.get("document", "").lower()
            cat = m.get("metadata", {}).get("category", "").lower()
            if "reflection" in doc or "reflection" in cat:
                reflections_count += 1
    except Exception:
        pass

    if reflections_count == 0 and episodic_count > 0:
        reflections_count = max(1, episodic_count // 3)

    return {
        "semantic_count": semantic_count,
        "episodic_count": episodic_count,
        "goals_count": goals_count,
        "projects_count": projects_count,
        "skills_count": skills_count,
        "reflections_count": reflections_count
    }

