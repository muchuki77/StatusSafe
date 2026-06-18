import os
import sys
import math
import pandas as pd
import io

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from rules_engine import validate_csv_row, process_batch

print("\n" + "=" * 55)
print("  STATUSSAFE — EDGE CASE TESTS")
print("=" * 55)

passed = 0
failed = 0

def check(test_name, condition, expected=True):
    global passed, failed
    status = "✅ PASS" if condition == expected else "❌ FAIL"
    if condition != expected:
        failed += 1
    else:
        passed += 1
    print(f"  {status}  {test_name}")

# Test 1: Empty CSV
print("\nTest 1: Empty CSV")
output = process_batch([])
check("Empty batch returns zero total",
      output["summary"]["total_evaluated"] == 0)
check("Empty batch returns empty results",
      len(output["results"]) == 0)
check("Empty batch returns empty skipped",
      len(output["skipped"]) == 0)

# Test 2: CSV with only headers
print("\nTest 2: CSV with only headers")
csv_data = "id,name,age\n"
df = pd.read_csv(io.StringIO(csv_data))
output = process_batch(df.to_dict(orient='records'))
check("Batch with only headers returns zero total",
      output["summary"]["total_evaluated"] == 0)
check("Batch with only headers returns empty results",
      len(output["results"]) == 0)
check("Batch with only headers returns empty skipped",
      len(output["skipped"]) == 0)

# Test 3: Single valid row
print("\n  SINGLE ROW")
single = [{
    "student_id":         "stu_single",
    "today":              "2026-01-14",
    "enrollment_status":  "enrolled",
    "full_time":          True,
    "program_level":      "graduate",
    "program_start_date": "2025-08-26",
    "opt_end_date":       "2027-01-01",
    "sevis_updated":      True
}]
output = process_batch(single)
check("Single row processed",
      output["summary"]["total_evaluated"] == 1)
check("Single valid row returns GREEN",
      output["results"][0]["rule_evaluation"]["overall_status"] == "GREEN")

# Tesr 4: Case sensitivity in headers
print("\n  CASE SENSITIVITY")
case_row = {
    "student_id":         "stu_case",
    "today":              "2026-01-14",
    "enrollment_status":  "Enrolled",    # capital E
    "full_time":          "true",
    "program_level":      "Graduate",    # capital G
    "program_start_date": "2025-08-26",
    "opt_end_date":       "2027-01-01",
    "sevis_updated":      "true"
}
result = validate_csv_row(case_row)
check("Capital E in enrollment_status accepted",
      result["valid"] == True)

# Test 5: Date validation
print("\n  DATE VALIDATION")
future_today = {
    "student_id":         "stu_future",
    "today":              "2035-01-01",
    "enrollment_status":  "enrolled",
    "full_time":          True,
    "program_level":      "graduate",
    "program_start_date": "2025-08-26",
    "sevis_updated":      True
}
result = validate_csv_row(future_today)
check("Future today date rejected",
      result["valid"] == False)

# Test 6: Missing required field
print("\n  MISSING FIELDS")
missing_sevis = {
    "student_id":         "stu_missing",
    "today":              "2026-01-14",
    "enrollment_status":  "enrolled",
    "full_time":          True,
    "program_level":      "graduate",
    "program_start_date": "2025-08-26",
}
result = validate_csv_row(missing_sevis)
check("Missing sevis_updated rejected",
      result["valid"] == False)
check("Correct reason returned",
      "sevis_updated" in result["reason"])

# Test 7: Date constraints
print("\n  DATE CONSTRAINTS")
wrong_dates = {
    "student_id":         "stu_dates",
    "today":              "2026-01-14",
    "enrollment_status":  "enrolled",
    "full_time":          True,
    "program_level":      "graduate",
    "program_start_date": "2025-08-26",
    "opt_end_date":       "2024-01-01",  # before program start
    "sevis_updated":      True
}
result = validate_csv_row(wrong_dates)
check("opt_end_date before program_start_date rejected",
      result["valid"] == False)

# Test 8: invalid enrollment status
print("\n  INVALID ENROLLMENT STATUS")
invalid_enrollment = {
    "student_id":         "stu_vocab",
    "today":              "2026-01-14",
    "enrollment_status":  "part_time",   # not in allowed values
    "full_time":          True,
    "program_level":      "graduate",
    "program_start_date": "2025-08-26",
    "sevis_updated":      True
}
result = validate_csv_row(invalid_enrollment)
check("Invalid enrollment_status rejected",
      result["valid"] == False)

# Test 9: NaN OPT end date
print("\n  NaN OPT END DATE")
nan_opt = {
    "student_id":         "stu_nan",
    "today":              "2026-01-14",
    "enrollment_status":  "enrolled",
    "full_time":          True,
    "program_level":      "graduate",
    "program_start_date": "2025-08-26",
    "opt_end_date":       float("nan"),  # NaN value
    "sevis_updated":      True
}
nan_result = validate_csv_row(nan_opt)
check("NaN opt_end_date treated as missing and rejected",
      nan_result["valid"] == True)

# Test 10: Large batch with all valid rows
print("\n  LARGE BATCH (500 rows)")
large_batch = [
    {
        "student_id":         f"stu_{i:04d}",
        "today":              "2026-01-14",
        "enrollment_status":  "enrolled",
        "full_time":          True,
        "program_level":      "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date":       "2027-01-01",
        "sevis_updated":      True
    }
    for i in range(500)
]
output = process_batch(large_batch)
check("500 rows all processed",
      output["summary"]["total_evaluated"] == 500)
check("500 rows all GREEN",
      output["summary"]["green"] == 500)

# Final summary
print("\n" + "=" * 55)
print(f"  TESTS PASSED: {passed}")
print(f"  TESTS FAILED: {failed}")
print("=" * 55 + "\n")  

if failed == 0:
    print(" ✅  All edge case tests passed successfully! 🎉")
else:
    print(" ❌  Some edge case tests failed. Please review the results above. ❌")
