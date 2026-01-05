## Purpose
This document defines the assumptions under which sevis bridge phase 1 rules engine operates. 
These assumptions establish clear boundaries for system behavior, data intepretaton and responsbility. 
The rules engine is designed ro flag administrative risk and not to determine legal or administratve status. 

## Data Assumptions
- Evaluation Context
- Each rule evaluation operates on a single student record at a single point in time.
- Records are evaluated independently; no historical or cross-student context is assumed.

## System Date
- Today represents the system evaluation date.
- Date comparisons are deterministic and use a consistent time reference.
- Phase 1 assumes all dates are provided in a comparable format (e.g., ISO-8601).

## Data fields assumed
Each rule evaluates a single student record with the following information
  - student-id -> No real student identifiers used
  - enrollment status -> (enrolled | not_enrolled) 
  - full time -> Boolean indicator of whether a student is enrolled full-time(true or false)
  - program level -> which academic level program (undergraduate | graduate)
  - program_start_date -> start date of the academic program which may also be in the future
  - opt-end-date -> end of OPT authorization if applicable
  - sevis updated -> Boolean indicator of whether SEVIS records have been updated to reflect the current or upcoming academic program (true | false)
## Data Validity Assumptions
- All required fields are present at evaluation time.
- Field values are syntactically valid (e.g., dates are parseable).
- The rules engine does not infer missing data.
- If required data is missing or invalid, evaluation fails explicitly rather than producing a risk classification.

## Behavioral assumptions
- All students are assumed to be acting in good faith.
- Administrative risk may arise from institutional or procedural gaps, not student intent.
- Rule triggers indicate potential issues requiring review, not wrongdoing.

## Non-assumptions
The system does not assume:
- Accuracy of institutional processes
- Legal correctness of enrollment or immigration status
- Real-time synchronization with SEVIS or university systems
- That enrollment implies immigration compliance
- That SEVIS updates occur automatically upon registration

## Rationale
These assumptions exist to:
- Ensure deterministic rule evaluation
- Support explainability and auditability
- Prevent implicit legal or institutional claims
- Enable safe extension in future phases
