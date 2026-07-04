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

# create a functon that gives StatusSafe its memory .
# Every time a batch assessment runs, this function write the batch assessment results to the database permanently.
# It needs to :
    # generate a unique batch_id for the assessment with a timestamp
    # Write one row to batches table with the batch_id, assessed_by, assessed_at, total_records, red_count, yellow_count, green_count, skipped_count
    # Write one row per student to assessments table with the batch_id, student_id, department, overall_status, triggered_rules, assessed_at
    # Write one row per triggered rule to rule_triggers table with the assessment_id, student_id, batch_id, rule_id, rule_name, severity, triggered_at
    # Return the batch_id for reference

def save_batch_results (output: dict, assessed_by: str = "DSO") -> str:
    """ 
    Save batch assessment results to the database.
    Returns batch id for reference.
    """

    # generate a unique batch_id for the assessment with a timestamp
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    assessed_at = datetime.now().isoformat()

    summary = output['summary']
    results  = output['results']

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()  

    # write batch summary
    cursor.execute("""
        INSERT INTO batches (batch_id, 
                   assessed_by, 
                   assessed_at, 
                   total_records,
                   red_count, 
                   yellow_count, 
                   green_count, 
                   skipped_count)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (batch_id, 
          assessed_by, 
          assessed_at, 
          summary['total_evaluated'], 
          summary['red'], 
          summary['yellow'], 
          summary['green'], 
          summary['skipped']))
    # write one row per student
    for r in results:
        triggered = [ x for x in  r["rule_evaluation"]["rule_results"] if x["status"] == "Triggered"]
        triggered_rules = ', '.join([x["name"] for x in triggered])
        cursor.execute("""
            INSERT INTO assessments (
                       batch_id,
                       student_id,
                       department,
                       overall_status,
                       triggered_rules,
                       assessed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (batch_id,
              r["student_id"],
              r.get("department", None),
              r["rule_evaluation"]["overall_status"],
              triggered_rules,
              assessed_at))
        
        assessment_id = cursor.lastrowid

        # write one row per triggered rule
        for rule in triggered:
            cursor.execute("""
                INSERT INTO rule_triggers (
                           assessment_id,
                           student_id,
                           batch_id,
                           rule_id,
                           rule_name,
                           severity,
                           triggered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (assessment_id,
                  r["student_id"],
                  batch_id,
                  rule["rule_id"],
                  rule["name"],
                  rule["severity"],
                  assessed_at))
    conn.commit()
    conn.close()
    return batch_id
              
                       
                    
                    
                       