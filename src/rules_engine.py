import math
from datetime import date
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Literal

RuleStatus = Literal['Pass', 'Triggered']
Severity = Literal['Info', 'Warning', 'Critical']

@dataclass
class RuleResult:
    rule_id: str
    name: str
    status: RuleStatus
    severity: Severity
    message: str
    recommended_action: str
    evidence: Dict[str, Any]    

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
def parse_iso_date(value:str, field_name:str) -> date:
    """
    Strict ISO date parsing.
    """
    try: 
        return date.fromisoformat(value)
    except ValueError as e:
        raise ValueError(f"{field_name} must be YYYY-MM-DD format") from e
    
# Rule R001: OPT ended without SEVIS update (Risk level: RED)
# Trigger: opt_end_date < today AND sevis_updated is False   
# If a student's OPT authorization has ended and there is no corresponding SEVIS update. 
# ** trigger condition ** opt-end-date is earlier than 'today' AND SEVIS-updated is false ** reason provided ** OPT ended but SEVIS record not updated. Recommended Action:
# Review SEVIS record and confirm next decision.

def rule_001_opt_ended_without_sevis_update(student_record: Dict[str, Any]) -> RuleResult:

    # Skip this rule if opt_end_date not provided
    if "opt_end_date" not in student_record or \
        student_record["opt_end_date"] == "":
        return RuleResult(
            rule_id="R001",
            name="OPT ended without SEVIS update",
            status="Pass",
            severity="Info",
            message="opt_end_date not provided — rule not applicable.",
            recommended_action="No action needed.",
            evidence={}
        )
    
    today = parse_iso_date(student_record['today'], 'today')
    opt_end_date = parse_iso_date(student_record["opt_end_date"], "opt_end_date")
    sevis_updated = student_record["sevis_updated"]

    triggered = (opt_end_date < today) and (sevis_updated is False)

    if triggered:
        return RuleResult(
            rule_id="R001",
            name="OPT ended without SEVIS update",
            status="Triggered",
            severity="Critical", # Risk level: RED
            message="OPT authorization has ended but SEVIS record not updated.",
            recommended_action="Review SEVIS record and confirm next decision.",
            evidence={
                "today": student_record["today"],
                "opt_end_date": student_record["opt_end_date"],
                "sevis_updated": sevis_updated,   
            },
        )
    return RuleResult(
        rule_id="R001",
        name="OPT ended without SEVIS update",
        status="Pass",
        severity="Info",
        message="No issues detected with OPT end date and SEVIS update.",
        recommended_action="No action needed.",
        evidence={
            "today": student_record["today"],
            "opt_end_date": student_record["opt_end_date"],
            "sevis_updated": sevis_updated,   
        },
    )

#####
#Risk Level: - RED Description:
#Enrollment in a new academic program without a recorded SEVIS program extension
# transfer may indicate misalignment between registration and immigration records. 
# Trigger Condition:
        #enrollment_status is "enrolled", AND  sevis_updated is false 
        # Reason Provided:student enrolled but SEVIS program extension not recorded. 
# OUTPUT: Severity: Critical
#Recommended action:Confirm SEVIS program dates and update records as needed. Confirm the change and program_start_date.

def rule_002_enrollment_without_sevis_program_extension_update(student_record: Dict[str, Any]) -> RuleResult:
    today = parse_iso_date(student_record['today'], 'today')
    enrollment_status = student_record["enrollment_status"]
    sevis_updated = student_record["sevis_updated"]

    triggered = (enrollment_status == "enrolled") and (sevis_updated is False)

    if triggered:
        return RuleResult(
            rule_id="R002",
            name="Enrollment without SEVIS update",
            status="Triggered",
            severity="Critical", # Risk level: RED
            message="Student enrolled but SEVIS program extension not recorded.",
            recommended_action="Confirm SEVIS program dates and update records as needed.",
            evidence={
                "today": student_record["today"],
                "enrollment_status": enrollment_status,
                "sevis_updated": sevis_updated,   
                "program_start_date": student_record["program_start_date"],
            },
        )
    return RuleResult(
        rule_id="R002",
        name="Enrollment without SEVIS update",
        status="Pass",
        severity="Info",
        message="No issues detected with enrollment status and SEVIS update.",
        recommended_action="No action needed.",
        evidence={
            "today": student_record["today"],
            "enrollment_status": enrollment_status,
            "sevis_updated": sevis_updated,   
        },
    )   

######
### Rule 3: OPT Grace Period Nearing Expiration
##Risk Level:** YELLOW
##Description:When a student is approaching the end of the OPT grace period without a confirmed SEVIS update, early attention can prevent downstream compliance issues.
##Trigger Condition: 
        ## - `opt_end_date` is within the last 60 days, AND  `sevis_updated` is false
##Reason Provided:OPT grace period nearing expiration without SEVIS update.
##Recommended Action:Review transition timeline and confirm next academic steps.

def rule_003_opt_grace_period_nearing_expiration(student_record: Dict[str, Any]) -> RuleResult:

    # Skip this rule if opt_end_date not provided
    if "opt_end_date" not in student_record or \
        student_record["opt_end_date"] == "":
        return RuleResult(
            rule_id="R003",
            name="OPT Grace Period Nearing Expiration",
            status="Pass",
            severity="Info",
            message="opt_end_date not provided — rule not applicable.",
            recommended_action="No action needed.",
            evidence={}
        )
    
    today = parse_iso_date(student_record['today'], 'today')
    opt_end = parse_iso_date(student_record["opt_end_date"], "opt_end_date")
    sevis_updated = student_record["sevis_updated"]

    days_until_opt_end = (opt_end - today).days
    triggered = (0 <= days_until_opt_end <= 60) and (sevis_updated is False) # there is a grace perions of 60 days

    if triggered:
        return RuleResult(
            rule_id="R003",
            name="OPT Grace Period Nearing Expiration",
            status="Triggered",
            severity="Warning", # Risk level: YELLOW
            message="OPT grace period nearing expiration without SEVIS update.",
            recommended_action="Review transition timeline and confirm next academic steps.",
            evidence={
                "today": student_record["today"],
                "opt_end_date": student_record["opt_end_date"],
                "sevis_updated": sevis_updated,   
            },
        )
    return RuleResult(
        rule_id="R003",
        name="OPT Grace Period Nearing Expiration",
        status="Pass",
        severity="Info",
        message="No issues detected with OPT grace period and SEVIS update.",
        recommended_action="No action needed.",
        evidence={
            "today": student_record["today"],
            "opt_end_date": student_record["opt_end_date"],
            "sevis_updated": sevis_updated,   
        },
    )
#####
# Rule 4: Under-Enrollment While on F-1
# Risk Level: YELLOW Description:F-1 students are generally required to maintain full-time enrollment. 
#            Under-enrollment without authorization may require review or documentation. 
# Trigger Condition:enrollment_status is "enrolled", AND  full_time is false 
# Reason Provided:Student is enrolled but not full time while maintaining F-1 status. 
# Recommended Action:Verify enrollment authorization or initiate corrective steps.
def rule_004_under_enrollment_while_on_f1(student_record: Dict[str, Any]) -> RuleResult:
    enrollment_status = student_record["enrollment_status"]
    full_time = student_record["full_time"]

    triggered = (enrollment_status == "enrolled") and (full_time is False)

    if triggered:
        return RuleResult(
            rule_id="R004",
            name="Under-Enrollment While on F-1",
            status="Triggered",
            severity="Warning", # Risk level: YELLOW
            message="Student is enrolled but not full time while maintaining F-1 status.",
            recommended_action="Verify enrollment authorization or initiate corrective steps.",
            evidence={
                "enrollment_status": enrollment_status,
                "full_time": full_time,   
            },
        )
    return RuleResult(
        rule_id="R004",
        name="Under-Enrollment While on F-1",
        status="Pass",
        severity="Info",
        message="No issues detected with enrollment status and full-time requirement.",
        recommended_action="No action needed.",
        evidence={
            "enrollment_status": enrollment_status,
            "full_time": full_time,   
        },
    )

#####
#Rule 5: No issues detected
#*** Risk level** GREEN Student is fully enrolled, has maintained F1 status with sevis record active and updated.
def rule_005_no_issues_detected(student_record: Dict[str, Any]) -> RuleResult:
    enrollment_status = student_record["enrollment_status"]
    full_time = student_record["full_time"]
    sevis_updated = student_record["sevis_updated"]

    triggered = not (enrollment_status == "enrolled" and full_time is True and sevis_updated is True)

    if triggered:
        return RuleResult(
            rule_id="R005",
            name="No Issues Detected",
            status="Pass",
            severity="Info", # Risk level: GREEN
            message="Student is fully enrolled, has maintained F1 status with SEVIS record active and updated.",
            recommended_action="No action needed.",
            evidence={
                "enrollment_status": enrollment_status,
                "full_time": full_time,
                "sevis_updated": sevis_updated,   
            },
        )
    return RuleResult(
        rule_id="R005",
        name="No Issues Detected",
        status="Pass",
        severity="Info",
        message="Some conditions for full compliance were not met",
        recommended_action="Review other triggered rules above",
        evidence={
            "enrollment_status": enrollment_status,
            "full_time": full_time,
            "sevis_updated": sevis_updated,   
        },
    )


def compute_overall_status(results: list[RuleResult]) -> str:
    for result in results:
        if result.status == "Triggered" and result.severity == "Critical":
            return "RED"
    for result in results:
        if result.status == "Triggered" and result.severity == "Warning":
            return "YELLOW"
    return "GREEN"


def evaluate_rules(student_record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Minimal phase 1 rule engine assumes that student record conforms to data_schema.md.
    """

    rules: List[Callable[[Dict[str, Any]], RuleResult]] = [
        rule_001_opt_ended_without_sevis_update,
        rule_002_enrollment_without_sevis_program_extension_update,
        rule_003_opt_grace_period_nearing_expiration,
        rule_004_under_enrollment_while_on_f1,
        rule_005_no_issues_detected,
        ]
    results = [rule(student_record)for rule in rules]
    overall = compute_overall_status(results)


    return {
        "overall_status": overall,
        "rule_results": [result.to_dict() for result in results],
    }

#####
def print_report(output: Dict[str, Any]) -> None:
    """
    Prints a clean, readable compliance report to the terminal.
    """
    status = output["overall_status"]
    results = output["rule_results"]

    # Status icons
    icons = {"RED": "🔴", "YELLOW": "🟡", "GREEN": "🟢"}
    severity_icons = {"Critical": "🔴", "Warning": "🟡", "Info": "🟢"}
    print("\n" + "=" * 55)
    print("  SEVIS BRIDGE — COMPLIANCE REPORT")
    print("=" * 55)
    print(f"  Overall Status: {icons.get(status, '')} {status}")
    print("=" * 55)

    # Triggered rules first
    triggered = [r for r in results if r["status"] == "Triggered"]
    passing = [r for r in results if r["status"] == "Pass"]

    if triggered:
        print("\n  ⚠️  TRIGGERED RULES:")
        for rule in triggered:
            icon = severity_icons.get(rule["severity"], "")
            print(f"\n  {icon} [{rule['rule_id']}] {rule['name']}")
            print(f"     Severity : {rule['severity']}")
            print(f"     Issue    : {rule['message']}")
            print(f"     Action   : {rule['recommended_action']}")
            print(f"     Evidence :")
            for key, value in rule["evidence"].items():
                print(f"               - {key}: {value}")

    if passing:
        print("\n  ✅  PASSING RULES:")
        for rule in passing:
            print(f"     • [{rule['rule_id']}] {rule['name']}")

    print("\n" + "=" * 55)
    print("  ⚠️  This tool does not provide legal advice.")
    print("  All data shown is for demonstration only.")
    print("=" * 55 + "\n")


#####
# Phase 2
def validate_csv_row(row: Dict[str, str]) -> Dict[str, Any]:
    """
    Validates a csv row aagainst phase 1 data schema.
    Returns a dict with ;
    - Valid :True or False
    - Reason: If not valid, provides reason for failure  and none if valid
    """
    required_fields = [
        "student_id", "today", "enrollment_status","full_time", "program_level", "program_start_date", "sevis_updated"
    ]

    valid_enrollment = ["enrolled", "not_enrolled"]
    valid_program    = ["undergraduate", "graduate"]

    # 1: check for all required fields
    for field in required_fields:
        if field not in row or row[field] == "":
            return {"valid": False, "reason": f"Missing required field: {field}"}
    # 2: Date format validation
    date_fields = ["today", "program_start_date"]
    parsed = {}
    for field in date_fields:
        try:
            parsed[field] = parse_iso_date(row[field], field)
        except ValueError:
            return {
                "valid": False,
                "reason": f"{field} must be in YYYY-MM-DD format"
            }
    
    # 3: Program start date must be <= today
    if parsed["program_start_date"] > parsed["today"]:
        return {
            "valid": False,
            "reason": "program_start_date cannot be in the future"
        }
    # 3 (b): today cannot be in the future
    if parsed["today"] > date.today():
        return {
            "valid": False,
            "reason": "today cannot be in the future"
        }
    
    # 4: validate opt date only if provided (opt_end_date is optional for students not on OPT)
    opt_val = row.get("opt_end_date", "")

    # treat pandas NaN as empty string for optional opt_end_date
    if isinstance(opt_val, float) and math.isnan(opt_val):
        # convert nan to empty string
        opt_val = "" 

    # validate if opt_end_date provided
    if opt_val != "":
        try:
            parsed["opt_end_date"] = date.fromisoformat(str(opt_val))
        except ValueError:
            return {
                "valid": False,
                "reason": "opt_end_date must be in YYYY-MM-DD format"
            }
        if parsed["opt_end_date"] < parsed["program_start_date"]:
            return {
                "valid": False,
                "reason": "opt_end_date cannot be before program_start_date"
            }
            

    # 5: enrollment status validation
    enrollment_val = str(row["enrollment_status"]).lower().strip()
    if enrollment_val not in valid_enrollment:
        return {
            "valid": False,
            "reason": f"enrollment_status must be one of {valid_enrollment}"
        }
    
    # 6: program level validation
    program_val = str(row["program_level"]).lower().strip()
    if program_val not in valid_program:
        return {
            "valid": False,
            "reason": f"program_level must be one of {valid_program}"
        }
    
    # 7: Boolean fields validation
    for bool_field in ["full_time", "sevis_updated"]:
        val = row[bool_field]
        if isinstance(val, str):
            if val.lower() not in ["true", "false"]:
                return {
                    "valid": False,
                    "reason": f"{bool_field} must be true or false"
                }

    return {"valid": True, "reason": None}

def process_batch(rows: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Processes a batch of CSV rows, validating each and
    evaluating rules for valid rows.
    Invalid rows are skipped and flagged — batch does not
    stop processing if invalid rows are encountered.
    """
    valid_results = []
    skipped_rows  = []

    for row in rows:

        # Step 1 — validate row
        validation = validate_csv_row(row)
        if not validation["valid"]:
            skipped_rows.append({
                "student_id":        row.get("student_id", "unknown"),
                "validation_status": "Failed",
                "validation_reason": validation["reason"],
                "rule_evaluation":   None
            })
            continue

        # Step 2 — normalise boolean fields
        for bool_field in ["full_time", "sevis_updated"]:
            val = row[bool_field]
            if isinstance(val, str):
                row[bool_field] = val.lower() == "true"
            elif isinstance(val, bool):
                pass
            else:
                row[bool_field] = bool(val)
        row["enrollment_status"] = row["enrollment_status"].lower().strip()
        row["program_level"] = row["program_level"].lower().strip()

        # Step 3 — handle NaN then build student record
        opt_val = row.get("opt_end_date", "")
        if isinstance(opt_val, float) and math.isnan(opt_val):
            opt_val = ""

        student_record = {
            "student_id":         row["student_id"],
            "today":              row["today"],
            "enrollment_status":  row["enrollment_status"],
            "full_time":          row["full_time"],
            "program_level":      row["program_level"],
            "program_start_date": row["program_start_date"],
            "opt_end_date":       opt_val,
            "sevis_updated":      row["sevis_updated"],
        }

        evaluation_output = evaluate_rules(student_record)

        # ONE append only
        valid_results.append({
            "student_id":        row["student_id"],
            "validation_status": "Passed",
            "validation_reason": None,
            "rule_evaluation":   evaluation_output
        })

    # Step 4 — outside the loop
    total   = len(valid_results)
    red     = sum(1 for r in valid_results
                  if r["rule_evaluation"]["overall_status"] == "RED")
    yellow  = sum(1 for r in valid_results
                  if r["rule_evaluation"]["overall_status"] == "YELLOW")
    green   = sum(1 for r in valid_results
                  if r["rule_evaluation"]["overall_status"] == "GREEN")
    skipped = len(skipped_rows)

    return {
        "summary": {
            "total_evaluated": total,
            "red":             red,
            "yellow":          yellow,
            "green":           green,
            "skipped":         skipped
        },
        "results": valid_results,
        "skipped": skipped_rows
    }
    
#####

if __name__ == "__main__":
    # Valid row
    good_row = {
        "student_id": "stu_001",
        "today": "2026-01-14",
        "enrollment_status": "enrolled",
        "full_time": True,
        "program_level": "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date": "2026-07-15",
        "sevis_updated": False
    }

    # Invalid row — missing field
    bad_row = {
        "student_id": "stu_002",
        "today": "2026-01-14",
        "enrollment_status": "enrolled",
        "full_time": True,
        "program_level": "graduate",
        "program_start_date": "2025-08-26",
        # opt_end_date missing
        "sevis_updated": False
    }

    print(validate_csv_row(good_row))
    print(validate_csv_row(bad_row))

