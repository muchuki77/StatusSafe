
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
        raise ValueError(f"{field_name} must be YYYY-MM-DD format!r") from e
    
# Rule R001: OPT ended without SEVIS update (Risk level: RED)
# Trigger: opt_end_date < today AND sevis_updated is False   
# If a student's OPT authorization has ended and there is no corresponding SEVIS update. 
# ** trigger condition ** opt-end-date is earlier than 'today' AND SEVIS-updated is false ** reason provided ** OPT ended but SEVIS record not updated. Recommended Action:
# Review SEVIS record and confirm next decision.

def rule_001_opt_ended_without_sevis_update(student_record: Dict[str, Any]) -> RuleResult:
    today = parse_iso_date(student_record['today'], 'today')
    opt_end = parse_iso_date(student_record["opt_end_date"], "opt_end_date")
    sevis_updated = student_record["sevis_updated"]

    triggered = (opt_end < today) and (sevis_updated is False)

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

#######################################################################################################################
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

##########################################################################################################################
### Rule 3: OPT Grace Period Nearing Expiration
##Risk Level:** YELLOW
##Description:When a student is approaching the end of the OPT grace period without a confirmed SEVIS update, early attention can prevent downstream compliance issues.
##Trigger Condition: 
        ## - `opt_end_date` is within the last 60 days, AND  `sevis_updated` is false
##Reason Provided:OPT grace period nearing expiration without SEVIS update.
##Recommended Action:Review transition timeline and confirm next academic steps.

def rule_003_opt_grace_period_nearing_expiration(student_record: Dict[str, Any]) -> RuleResult:
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
#####################################################################################################
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

#####################################################################################################
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
        message="No issues detected with enrollment status, full-time requirement, and SEVIS update.",
        recommended_action="No action needed.",
        evidence={
            "enrollment_status": enrollment_status,
            "full_time": full_time,
            "sevis_updated": sevis_updated,   
        },
    )

#####################################################################################################
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

if __name__ == "__main__":
    student_record = {
        "student_id": "stu_smoke_001",
        "today": "2026-01-14",
        "enrollment_status": "enrolled",
        "full_time": True,
        "program_level": "graduate",
        "program_start_date": "2025-08-26",
        "opt_end_date": "2026-07-15",
        "sevis_updated": False
    }
    output = evaluate_rules(student_record)
    print(output)

