import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'frieren_state.db')

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes the database schema."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # User Profile
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS UserProfile (
        id INTEGER PRIMARY KEY,
        name TEXT,
        speaking_style_preference TEXT,
        last_interaction DATETIME
    )
    """)
    
    # Interests
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Interests (
        id INTEGER PRIMARY KEY,
        profile_id INTEGER,
        interest TEXT,
        weight FLOAT
    )
    """)
    
    # Goals
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Goals (
        id INTEGER PRIMARY KEY,
        title TEXT,
        description TEXT,
        type TEXT,
        status TEXT,
        associated_project TEXT,
        created_at DATETIME,
        updated_at DATETIME
    )
    """)
    
    # Projects
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Projects (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        status TEXT,
        created_at DATETIME
    )
    """)
    
    # Skills
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Skills (
        id INTEGER PRIMARY KEY,
        skill_name TEXT UNIQUE,
        category TEXT,
        level TEXT,
        progress INTEGER,
        last_updated DATETIME
    )
    """)
    
    # Conversations
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Conversations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        device_id TEXT,
        session_id TEXT,
        user_message TEXT,
        ai_response TEXT,
        timestamp DATETIME
    )
    """)
    
    # RepresentativeTasks
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS RepresentativeTasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_description TEXT,
        status TEXT,
        result TEXT,
        created_at DATETIME,
        updated_at DATETIME
    )
    """)
    
    # Seed representative tasks if empty
    cursor.execute("SELECT COUNT(*) FROM RepresentativeTasks")
    if cursor.fetchone()[0] == 0:
        from datetime import datetime
        now = datetime.now().isoformat()
        cursor.execute("INSERT INTO RepresentativeTasks (task_description, status, result, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                       ("Research Topic: Advanced progressive web apps in 2026", "completed", "Found 12 research papers on offline syncing and WebGPU service workers.", now, now))
        cursor.execute("INSERT INTO RepresentativeTasks (task_description, status, result, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                       ("Generate Report: Frieren memory usage telemetry", "completed", "Telemetry indicates episodic collection has 89 nodes, semantic has 214 nodes.", now, now))
        cursor.execute("INSERT INTO RepresentativeTasks (task_description, status, result, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                       ("Draft Email: Weekly progress to user", "pending", None, now, now))
    
    conn.commit()
    conn.close()


# Initialize DB on import
init_db()
