# SEVIS-bridge compliance rules
## Purpose
This document defines the initial set of rule-based checks used by SEVIS Bridge to identify potential administrative or compliance risks related to F-1 student status during common academic transitions.
These rules are **preventive and advisory** in nature. They do not determine legal status and are intended to support institutional review and early intervention.

## Design principles
1. All students are assumed to be acting in good faith
2. Rules flag risks not violations
3. outputs are explainable and auditable
4. no real sevis or student data is used
5. This does provide leagl advice

## Risk levels
green - no immediate administrative risk detected
yellow - Attention needed, time sensitive but typically correctable
red - Immediate administrative review recommended

N/B If mulitple rules apply, the highest risk level takes precedence

## RULES SET

### Rule 1 - OPT ended without SEVIS update
**Risk level - RED
If a student's OPT authorization has ended and there is no corresponding SEVIS update.
** trigger condition **
opt-end-date is earlier than 'today' AND SEVIS-updated is false
** reason provided **
OPT ended but SEVIS record not updated.
**Recommended Action:**  
Review SEVIS record and confirm next decision. 

### Rule 2: Enrollment Without Program Extension Update
**Risk Level:** - RED
**Description:**  
Enrollment in a new academic program without a recorded SEVIS program extension or transfer may indicate misalignment between registration and immigration records.
**Trigger Condition:**  
- `enrollment_status` is "enrolled", AND  `sevis_updated` is false
**Reason Provided:**  
 Student enrolled but SEVIS program extension not recorded.
**Recommended Action:**  
- Confirm SEVIS program dates and update records as needed. Confirm the change and program_start_date.

### Rule 3: OPT Grace Period Nearing Expiration
**Risk Level:** YELLOW
**Description:**  
When a student is approaching the end of the OPT grace period without a confirmed SEVIS update, early attention can prevent downstream compliance issues.
**Trigger Condition:**  
- `opt_end_date` is within the last 60 days, AND  `sevis_updated` is false
**Reason Provided:**  
 OPT grace period nearing expiration without SEVIS update.
**Recommended Action:**  
- Review transition timeline and confirm next academic steps.
- 

### Rule 4: Under-Enrollment While on F-1
**Risk Level:** YELLOW
**Description:**  
F-1 students are generally required to maintain full-time enrollment. Under-enrollment without authorization may require review or documentation.
**Trigger Condition:**  
- `enrollment_status` is "enrolled", AND  `full_time` is false
**Reason Provided:**  
Student is enrolled but not full time while maintaining F-1 status.
**Recommended Action:**  
- Verify enrollment authorization or initiate corrective steps.

### Rule 5: No issues detected
*** Risk level** GREEN
Student is fully enrolled, has maintained F1 status with sevis record active and updated. 


## Rule Evaluation Logic
- Each student record is evaluated independently.
- All applicable rules are logged.
- Only one reason is surfaced to the user to avoid confusion.
- The highest risk rules determined the displayed status


## Future Enhancements
- Severity escalation based on duration.
- Additional transition scenarios (leave of absence, program deferral).
- Configurable grace period thresholds.
- Analytics on recurring institutional failure points.

