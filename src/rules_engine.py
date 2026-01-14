
from datetime import date
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Literal

RuleStatus = Literal['Pass', 'Triggered']
Severity = Literal['Info', 'Warning', 'Critical']


class RuleResult:
    rule_id: str
    name: str
    status: RuleStatus
    severity: Severity
    message: str
    recommned_action: str
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
            recommned_action="Review SEVIS record and confirm next decision.",
            evidence={
                "today": student_record("today"),
                "opt_end_date": student_record("opt_end_date"),
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
            "today": student_record("today"),
            "opt_end_date": student_record("opt_end_date"),
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
        rule_002_enrollment_without_sevis_program_extension_update,]
    results = [rule(student_record)for rule in rules]
    overall = compute_overall_status(results)


    return {
        "overall_status": overall,
        "rule_results": [result.to_dict() for result in results],
    }

if __name__ == "___main__":
    student_record = {
        "student_id": "stu_smoke_001",
        "today": "2026-01-14",
        "enrollment_status": "enrolled",
        "full_time": True,
        "program_level": "graduate",
        "prgram_start_date": "2025-08-26",
        "opt_end_date": "2026-07-15",
        "sevis_updated": False
    }
    output = evaluate_rules(student_record)
    print(output)


if __name__ == "__main__":
    print("hello")


#####################################################################################################

#Risk Level: - RED Description:
#Enrollment in a new academic program without a recorded SEVIS program extension
# transfer may indicate misalignment between registration and immigration records. 
# Trigger Condition:
        #enrollment_status is "enrolled", AND  sevis_updated is false 
        # Reason Provided:student enrolled but SEVIS program extension not recorded. 
# OUTPUT: Severity: Critical
#Recommended action:Confirm SEVIS program dates and update records as needed. Confirm the change and program_start_date.

def rule_002_enrollment_without_sevis_program_extension_update(student_record: Dict[str, any]) -> RuleResult:
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
                "today": student_record("today"),
                "enrollment_status": enrollment_status,
                "sevis_updated": sevis_updated,   
                "program_start_date": student_record("program_start_date"),
            },
        )
    return RuleResult(
        rule_id="R002",
        name="Enrollment without SEVIS update",
        status="Pass",
        severity="Info",
        message="No issues detected with enrollment status and SEVIS update.",
        recommned_action="No action needed.",
        evidence={
            "today": student_record("today"),
            "enrollment_status": enrollment_status,
            "sevis_updated": sevis_updated,   
        },
    )   

