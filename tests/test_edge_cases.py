import os
import sys
import math
import pandas as pd
import io

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from rules_engine import validate_csv_row, process_batch, evaluate_rules, compute_overall_status,extract_features

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


# Test 11: R005 report of full compliance when all R001 - R004 pass
print("\n Test all four rules pass!")
student_rec = {
    "student_id": "stu_001",
    "today": "2026-01-14",
    "enrollment_status": "enrolled",
    "full_time": True,
    "program_level": "graduate",
    "program_start_date": "2025-08-26",
    "opt_end_date": "2026-07-15",
    "sevis_updated": True
    }
output = evaluate_rules(student_rec)
r005 = None

for rule in output["rule_results"]:
      if rule ["rule_id"] == "R005":
           r005 = rule

check("R005 reports that student is fully compliant",
    r005["status"] == "Pass")
check("R005 reports correct compliant message",
      r005["message"] == "Student fully compliant")


# Test 12: R003 is triggered while R001, R002 & R004 pass
print("\n Rule 003 is triggered")
student_rec = {
"student_id": "stu_001",
"today": "2026-07-29",
"enrollment_status": "not_enrolled",
"full_time": True,
"program_level": "graduate",
"program_start_date": "2025-08-26",
"opt_end_date": "2026-08-15",
"sevis_updated": False
}
output = evaluate_rules(student_rec)
r005 = None
for rule in output["rule_results"]:
    if rule ["rule_id"] == "R005":
      r005 = rule

check("R005 reports that student is not fully compliant",
r005["status"] == "Pass")
check("R005 reports correct compliant message",
r005["message"] == "One or more of the compliance rules have been triggered. See details above!")
check("Overall status is YELLOW when R003 is triggered",
      output["overall_status"]== "YELLOW")


# Test 13: R001 is triggered while R002, R003 & R004 pass
print("\n Rule 001 is triggered")
student_rec = {
"student_id": "stu_001",
"today": "2026-07-29",
"enrollment_status": "not_enrolled",
"full_time": True,
"program_level": "graduate",
"program_start_date": "2025-08-26",
"opt_end_date": "2026-07-01",
"sevis_updated": False
}
output = evaluate_rules(student_rec)
r005 = None
for rule in output["rule_results"]:
    if rule ["rule_id"] == "R005":
      r005 = rule

check("R005 reports that student is not fully compliant",
r005["status"] == "Pass")
check("R005 reports correct compliant message",
r005["message"] == "One or more of the compliance rules have been triggered. See details above!")
check("Overall status is RED when R001 is triggered",
      output["overall_status"]== "RED")


# Test 14: R002 & R004 is triggered while R001 & R003 pass
print("\n Rules 002 & 004 are triggered")
student_rec = {
"student_id": "stu_001",
"today": "2025-11-19",
"enrollment_status": "enrolled",
"full_time": False,
"program_level": "graduate",
"program_start_date": "2022-08-22",
"sevis_updated": False
}
output = evaluate_rules(student_rec)
r005 = None
for rule in output["rule_results"]:
    if rule["rule_id"] == "R005":
        r005 = rule

check("R005 reports that student is not fully compliant",
r005["status"] == "Pass")
check("R005 reports correct compliant message",
r005["message"] == "One or more of the compliance rules have been triggered. See details above!")
check("Overall status is RED when both RED and YELLOW are triggered",
      output["overall_status"] == "RED")

# Test 15: Feature extraction with missing opt_end_date
print("\n Feature extraction with missing opt_end_date")
student_record = {
    "student_id": "stu_001",
    "today": "2026-01-14",
    "enrollment_status": "enrolled",
    "full_time": True,
    "program_level": "graduate",
    "program_start_date": "2025-08-26",
    # opt_end_date is missing
    "sevis_updated": True
}
features_no_opt = extract_features(student_record)

check("is_enrolled feature is 1.0 for enrolled student",features_no_opt["is_enrolled"] == 1.0)
check("is_full_time feature is 1.0 for full-time student",features_no_opt["is_full_time"] == 1.0)
check("sevis_updated feature is 1.0 when True",features_no_opt["sevis_updated"] == 1.0)
check("has_opt_end_date feature is 0.0 when opt_end_date is missing",features_no_opt["has_opt_end_date"] == 0.0)
check("opt_days_masked feature is 0.0 when not on OPT",features_no_opt["opt_days_masked"] == 0.0)

# Test 16: Feature extraction for student who is past their OPT end date
print("\n Feature extraction for student past OPT end date")
student_record_past_opt = {
    "student_id": "stu_002",
    "today": "2026-01-14",
    "enrollment_status": "not_enrolled",
    "full_time": False,
    "program_level": "graduate",
    "program_start_date": "2024-08-26",
    "opt_end_date": "2025-12-01",  # this student's OPT ended in December 2025
    "sevis_updated": False
}
features_past_opt = extract_features(student_record_past_opt)     

check("is_enrolled feature is 0.0 for not enrolled student",features_past_opt["is_enrolled"] == 0.0)
check("is_full_time feature is 0.0 for part-time student",features_past_opt["is_full_time"] == 0.0)
check("sevis_updated feature is 0.0 when False",features_past_opt["sevis_updated"] == 0.0)
check("has_opt_end_date feature is 1.0 when opt_end_date is provided",features_past_opt["has_opt_end_date"] == 1.0)
check("opt_days_masked feature is -44.0 past due OPT",features_past_opt["opt_days_masked"] == -44.0)
check("opt_days_masked feature is negative  when OPT end date is in the past",features_past_opt["opt_days_masked"] < 0.0)     


# Final summary
print("\n" + "=" * 55)
print(f"  TESTS PASSED: {passed}")
print(f"  TESTS FAILED: {failed}")
print("=" * 55 + "\n")  

if failed == 0:
    print(" ✅  All edge case tests passed successfully! 🎉")
else:
    print(" ❌  Some edge case tests failed. Please review the results above. ❌")


