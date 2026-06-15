from fastapi import APIRouter, Depends, Query
from db.database import get_connection
from backend.auth.security import get_api_key
from typing import Optional

router = APIRouter(prefix="/api/v1/conversations", dependencies=[Depends(get_api_key)])

@router.get("")
async def get_conversations(
    date: Optional[str] = Query(None, description="Date filter (YYYY-MM-DD)"),
    session_id: Optional[str] = Query(None, description="Session ID filter"),
    device_id: Optional[str] = Query(None, description="Device ID filter")
):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM Conversations WHERE 1=1"
        params = []
        
        if date:
            query += " AND timestamp LIKE ?"
            params.append(f"{date}%")
            
        if session_id:
            query += " AND session_id = ?"
            params.append(session_id)
            
        if device_id:
            query += " AND device_id = ?"
            params.append(device_id)
            
        query += " ORDER BY id DESC LIMIT 100"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "id": row["id"],
                "user_id": row["user_id"],
                "device_id": row["device_id"],
                "session_id": row["session_id"],
                "user_message": row["user_message"],
                "ai_response": row["ai_response"],
                "timestamp": row["timestamp"]
            })
        return results
    except Exception as e:
        print(f"[!] Conversations endpoint error: {e}")
        return []
