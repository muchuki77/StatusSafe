import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from database import (
    get_batch_history,
    get_most_common_rules,
    get_repeat_alerts
)

print("\n" + "=" * 55)
print("  STATUSSAFE — QUERY FUNCTION TESTS")
print("=" * 55)

# Batch history
history = get_batch_history()
print(f"\n  Batch history: {len(history)} batches found")
for batch in history:
    print(f"  • {batch['batch_id']} — "
          f"RED:{batch['red_count']} "
          f"YELLOW:{batch['yellow_count']} "
          f"GREEN:{batch['green_count']}")

# Most common rules
rules = get_most_common_rules()
print(f"\n  Most common triggered rules:")
for rule in rules:
    print(f"  • {rule['rule_id']} {rule['rule_name']} "
          f"— {rule['frequency']} times")

# Repeat alerts
repeats = get_repeat_alerts()
print(f"\n  Repeat alerts: {len(repeats)} students")
for student in repeats:
    print(f"  • {student['student_id']} "
          f"flagged {student['alert_count']} times")

print("\n" + "=" * 55 + "\n")