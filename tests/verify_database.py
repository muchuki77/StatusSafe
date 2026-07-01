# this is a database verification script
import sqlite3
import os
import sys

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, PROJECT_ROOT)

DB_PATH = os.path.join(PROJECT_ROOT, 'data', 'statussafe.db')

# Check database file exists
if not os.path.exists(DB_PATH):
    print(f"❌ Database file not found at {DB_PATH}")
    print("   Run python src/database.py first to initialise it.")
else:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    conn.close()

    print("\n" + "=" * 55)
    print("  STATUSSAFE — DATABASE VERIFICATION")
    print("=" * 55)
    print(f"  Database: {DB_PATH}")
    print(f"\n  Tables found: {len(tables)}")
    for table in tables:
        print(f"  ✅  {table[0]}")

    expected = {"batches", "assessments", "rule_triggers", "resolutions"}
    found = {t[0] for t in tables if not t[0].startswith("sqlite_")}  # Exclude internal SQLite tables

    if expected == found:
        print("\n  ✅  All four tables present.")
    else:
        missing = expected - found
        print(f"\n  ❌  Missing tables: {missing}")

    print("=" * 55 + "\n")
