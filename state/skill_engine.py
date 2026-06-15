from db.database import get_connection
from datetime import datetime
from typing import List, Dict

class SkillEngine:
    def __init__(self):
        self._initialize_core_skills()

    def _initialize_core_skills(self):
        """Seed the database with the user's requested trackable skills if they don't exist."""
        core_skills = [
            ("SQL", "Data", "Beginner", 0),
            ("Python", "Programming", "Beginner", 0),
            ("Power BI", "Data Analytics", "Beginner", 0),
            ("Data Analytics", "Domain", "Beginner", 0),
            ("Machine Learning", "AI", "Beginner", 0)
        ]
        
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        for skill_name, category, level, progress in core_skills:
            cursor.execute("""
                INSERT OR IGNORE INTO Skills (skill_name, category, level, progress, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (skill_name, category, level, progress, now))
        
        conn.commit()
        conn.close()

    def add_skill(self, skill_name: str, category: str = "General", level: str = "Beginner", progress: int = 0):
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute("""
            INSERT OR IGNORE INTO Skills (skill_name, category, level, progress, last_updated)
            VALUES (?, ?, ?, ?, ?)
        """, (skill_name, category, level, progress, now))
        conn.commit()
        conn.close()

    def update_skill_progress(self, skill_name: str, progress_increment: int):
        """Increase the progress of a skill."""
        conn = get_connection()
        cursor = conn.cursor()
        now = datetime.now().isoformat()
        
        # Fetch current
        cursor.execute("SELECT progress FROM Skills WHERE skill_name = ?", (skill_name,))
        row = cursor.fetchone()
        if row:
            new_progress = min(100, row['progress'] + progress_increment)
            
            # Simple level progression logic
            new_level = "Beginner"
            if new_progress >= 40: new_level = "Intermediate"
            if new_progress >= 80: new_level = "Advanced"
            
            cursor.execute("""
                UPDATE Skills SET progress = ?, level = ?, last_updated = ?
                WHERE skill_name = ?
            """, (new_progress, new_level, now, skill_name))
            conn.commit()
        conn.close()

    def get_all_skills(self) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Skills ORDER BY progress DESC")
        skills = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return skills
        
    def get_fastest_progressing_skills(self) -> List[Dict]:
        conn = get_connection()
        cursor = conn.cursor()
        # Proxying "fastest progressing" by sorting by last_updated and progress
        cursor.execute("SELECT * FROM Skills WHERE progress > 0 ORDER BY last_updated DESC, progress DESC LIMIT 3")
        skills = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return skills
