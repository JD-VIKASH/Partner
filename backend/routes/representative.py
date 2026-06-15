from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from db.database import get_connection
from backend.auth.security import get_api_key
from core.representative_engine import RepresentativeEngine
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/representative", dependencies=[Depends(get_api_key)])
engine = RepresentativeEngine()

class TaskRequest(BaseModel):
    task_description: str

def run_representative_task_background(task_id: int, description: str):
    import time
    # Simulate realistic delay
    time.sleep(2.0)
    try:
        success = engine.execute_on_behalf(description)
        status = "completed" if success else "failed"
        result_text = f"Action successfully executed at {datetime.now().strftime('%H:%M:%S')}. Representative Engine confirmed completion." if success else "Execution failed."
    except Exception as e:
        status = "failed"
        result_text = f"Error: {str(e)}"

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE RepresentativeTasks SET status = ?, result = ?, updated_at = ? WHERE id = ?",
            (status, result_text, datetime.now().isoformat(), task_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[!] Failed to update background task status in SQLite: {e}")

@router.get("/tasks")
async def get_tasks():
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM RepresentativeTasks ORDER BY id DESC")
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "task_description": row["task_description"],
                "status": row["status"],
                "result": row["result"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            })
        return results
    except Exception as e:
        print(f"[!] Representative get_tasks error: {e}")
        return []

@router.post("/tasks")
async def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO RepresentativeTasks (task_description, status, result, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
            (request.task_description, "pending", None, now, now)
        )
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        background_tasks.add_task(run_representative_task_background, task_id, request.task_description)
        
        return {
            "status": "success",
            "message": "Task queued for execution.",
            "task": {
                "id": task_id,
                "task_description": request.task_description,
                "status": "pending",
                "result": None,
                "created_at": now,
                "updated_at": now
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to queue task: {str(e)}")
