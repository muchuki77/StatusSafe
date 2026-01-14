
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
        recommned_action="No action needed.",
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

    rules: List[Callable[[Dict[str, Any]], RuleResult]] = [rule_001_opt_ended_without_sevis_update]
    results = [rule(student_record)for rule in rules]
    overall = compute_overall_status(results)


    return {
        "overall_status": overall,
        "rule_results": [result.to_dict() for result in results],
    }

if __name__ == "___main__":
    sample_student_record = {
        "student_id": "S12345678",
        "today": "2024-06-15",
        "enrollment_status": "enrolled",
        "full_time": True,
        "program_level": "graduate",
        "prgram_start_date": "2022-09-01",
        "opt_end_date": "2024-05-30",
        "sevis_updated": False,
    }

    output = evaluate_rules(sample_student_record)
    print(output)

    






