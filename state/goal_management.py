from db.database import get_connection
from datetime import datetime
from typing import List, Dict, Optional

class GoalManagementSystem:
    def add_goal(self, title: str, description: str, goal_type: str, associated_project: Optional[str] = None):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO Goals (title, description, type, status, associated_project, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (title, description, goal_type, 'active', associated_project, now, now)
        )
        conn.commit()
        conn.close()

    def get_active_goals(self) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Goals WHERE status = 'active'")
        goals = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return goals

    def complete_goal(self, goal_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Goals SET status = 'completed', updated_at = ? WHERE id = ?", 
                       (datetime.now().isoformat(), goal_id))
        conn.commit()
        conn.close()
