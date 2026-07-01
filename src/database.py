import os
import sqlite3
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(__file__), '..','data','statussafe.db')

def init_database():
    """
    Create StatusSafe database and all the required tables if they do not already exist
    """

    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor() # cursor is the tool used to run sql commands 

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS batches(
                   batch_id  TEXT PRIMARY KEY,
                   assessed_by TEXT,
                   assessed_at TEXT NOT NULL,
                   total_records INTEGER,
                   red_count INTEGER,
                   yellow_count INTEGER,
                   green_count INTEGER,
                   skipped_count INTEGER
                   )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assessments(
                   id           INTEGER PRIMARY KEY AUTOINCREMENT,
                   batch_id     TEXT NOT NULL,
                   student_id   TEXT NOT NULL,
                   department   TEXT,
                   overall_status TEXT NOT NULL,
                   triggered_rules TEXT,
                   assessed_at TEXT NOT NULL,
                   FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
                   )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rule_triggers(
                   id            INTEGER PRIMARY KEY AUTOINCREMENT,
                   assessment_id INTEGER NOT NULL,
                   student_id    TEXT NOT NULL,
                   batch_id      TEXT NOT NULL,
                   rule_id       TEXT NOT NULL,
                   rule_name     TEXT NOT NULL,
                   severity      TEXT NOT NULL,
                   triggered_at  TEXT NOT NULL,
                   FOREIGN KEY (assessment_id) REFERENCES assessments(id)
                   )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resolutions(
                   id            INTEGER PRIMARY KEY AUTOINCREMENT,
                   student_id    TEXT NOT NULL,
                   rule_id       TEXT NOT NULL,
                   assessment_id INTEGER NOT NULL,
                   resolved_by   TEXT,
                   resolved_at   TEXT NOT NULL,
                   notes         TEXT,
                   FOREIGN KEY (assessment_id) REFERENCES assessments(id)
                   )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {DB_PATH}")

if __name__ == "__main__":
    init_database()
