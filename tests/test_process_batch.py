import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, PROJECT_ROOT)

from src.rules_engine import process_batch

rows = [
    # Valid — RED
    {
        "student_id": "stu_001",
        "today": "2026-01-14",
        "enrollment_status": "enrolled",
        "full_time": "true",
        "program_level": "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date": "2025-12-01",
        "sevis_updated": "false"
    },
    # Valid — GREEN
    {
        "student_id": "stu_002",
        "today": "2026-01-14",
        "enrollment_status": "enrolled",
        "full_time": "true",
        "program_level": "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date": "2027-01-01",
        "sevis_updated": "true"
    },
    # Invalid — missing sevis_updated
    {
        "student_id": "stu_003",
        "today": "2026-01-14",
        "enrollment_status": "enrolled",
        "full_time": "true",
        "program_level": "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date": "2027-01-01"
    },
]

output = process_batch(rows)

print("\n" + "=" * 55)
print("  BATCH PROCESSING TEST")
print("=" * 55)
print(f"  Total evaluated : {output['summary']['total_evaluated']}")
print(f"  RED             : {output['summary']['red']}")
print(f"  YELLOW          : {output['summary']['yellow']}")
print(f"  GREEN           : {output['summary']['green']}")
print(f"  Skipped         : {output['summary']['skipped']}")
print("\n  Results:")
for r in output["results"]:
    print(f"  • {r['student_id']} → {r['rule_evaluation']['overall_status']}")
print("\n  Skipped:")
for s in output["skipped"]:
    print(f"  • {s['student_id']} → {s['validation_reason']}")
print("=" * 55 + "\n")