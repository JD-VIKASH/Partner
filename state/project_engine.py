from db.database import get_connection
from datetime import datetime
from typing import List, Dict

class ProjectEngine:
    def add_project(self, name: str, description: str):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO Projects (name, description, status, created_at) VALUES (?, ?, ?, ?)",
            (name, description, 'active', now)
        )
        conn.commit()
        conn.close()

    def get_active_projects(self) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Projects WHERE status = 'active'")
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return projects

    def complete_project(self, project_id: int):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE Projects SET status = 'completed' WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()
