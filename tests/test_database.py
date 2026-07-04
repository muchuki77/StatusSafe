import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from database import init_database, save_batch_results
from rules_engine import process_batch

import sqlite3

# Initialise database
init_database()

# Create a small test batch
rows = [
    {
        "student_id":         "stu_test_001",
        "today":              "2026-01-14",
        "enrollment_status":  "enrolled",
        "full_time":          True,
        "program_level":      "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date":       "2025-12-01",
        "sevis_updated":      False
    },
    {
        "student_id":         "stu_test_002",
        "today":              "2026-01-14",
        "enrollment_status":  "enrolled",
        "full_time":          True,
        "program_level":      "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date":       "2027-01-01",
        "sevis_updated":      True
    }
]

output = process_batch(rows)
batch_id = save_batch_results(output, assessed_by="test_dso")

# Verify it was saved
DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'statussafe.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT * FROM batches WHERE batch_id = ?", (batch_id,))
batch = cursor.fetchone()

cursor.execute(
    "SELECT * FROM assessments WHERE batch_id = ?", (batch_id,)
)
assessments = cursor.fetchall()

cursor.execute(
    "SELECT * FROM rule_triggers WHERE batch_id = ?", (batch_id,)
)
triggers = cursor.fetchall()

conn.close()

print("\n" + "=" * 55)
print("  DATABASE SAVE TEST")
print("=" * 55)
print(f"  Batch ID      : {batch_id}")
print(f"  Batch saved   : {'✅' if batch else '❌'}")
print(f"  Assessments   : {len(assessments)} rows")
print(f"  Rule triggers : {len(triggers)} rows")
print("=" * 55 + "\n")