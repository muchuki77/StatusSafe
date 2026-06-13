import json
import sys
import os

# Build the project rood relative to the scrpt's location
# scrpt  location: tests/verify_all_samples.py
# Project root is one level up .../
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# add project root to python path so imports work
sys.path.insert(0,PROJECT_ROOT)

# build sample paths from  the project root
SAMPLES_DIR = os.path.join(PROJECT_ROOT, "samples")

from src.rules_engine import evaluate_rules

samples = [
    os.path.join(SAMPLES_DIR, "student_red_rule1.json"),
    os.path.join(SAMPLES_DIR, "student_red_rule2.json"),
    os.path.join(SAMPLES_DIR, "student_yellow_rule3.json"),
    os.path.join(SAMPLES_DIR, "student_yellow_rule4.json"),
    os.path.join(SAMPLES_DIR, "student_green_rule5.json"),
    os.path.join(SAMPLES_DIR, "student_precedence_red_over_yellow.json"),
    os.path.join(SAMPLES_DIR, "student_enrolled_no_opt.json"),
]

expected = {
    "student_red_rule1.json": "RED",
    "student_red_rule2.json": "RED",
    "student_yellow_rule3.json": "YELLOW",
    "student_yellow_rule4.json": "YELLOW",
    "student_green_rule5.json": "GREEN",
    "student_precedence_red_over_yellow.json": "RED",
    "student_enrolled_no_opt.json": "GREEN",
}

print("\n" + "=" * 55)
print("  SEVIS BRIDGE — SAMPLE VERIFICATION")
print("=" * 55)

all_passed = True

for path in samples:
    filename = os.path.basename(path)
    
    with open(path) as f:
        student = json.load(f)
    
    result = evaluate_rules(student)
    actual = result["overall_status"]
    exp = expected[filename]
    passed = actual == exp
    
    if not passed:
        all_passed = False
    
    status_icon = "✅" if passed else "❌"
    print(f"  {status_icon}  {filename:<45} → {actual} (expected {exp})")

print("=" * 55)
if all_passed:
    print("  ✅  All samples passed verification.")
else:
    print("  ❌  Some samples failed. Review engine logic.")
print("=" * 55 + "\n")

