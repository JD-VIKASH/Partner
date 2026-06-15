from db.database import get_connection
from datetime import datetime
import json

class UserProfileEngine:
    def __init__(self):
        # Ensure a default profile exists
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM UserProfile")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO UserProfile (name, speaking_style_preference, last_interaction) VALUES (?, ?, ?)",
                           ("User", "calm", datetime.now().isoformat()))
            conn.commit()
        conn.close()

    def get_profile(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM UserProfile ORDER BY id DESC LIMIT 1")
        profile = dict(cursor.fetchone())
        
        cursor.execute("SELECT interest, weight FROM Interests WHERE profile_id = ?", (profile['id'],))
        interests = [{"interest": r["interest"], "weight": r["weight"]} for r in cursor.fetchall()]
        profile['interests'] = interests
        conn.close()
        return profile

    def update_preference(self, key: str, value: str):
        # Simplistic approach: Update speaking style specifically or store extra in a JSON column if we add one.
        conn = get_connection()
        cursor = conn.cursor()
        if key == "speaking_style_preference":
            cursor.execute("UPDATE UserProfile SET speaking_style_preference = ?, last_interaction = ?", 
                           (value, datetime.now().isoformat()))
        conn.commit()
        conn.close()
