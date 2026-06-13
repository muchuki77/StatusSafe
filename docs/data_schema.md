## PHASE 1
### Purpose
- The schema defines the exact fields required in phase 1 of SevisBridge
- Each file evaluates one student record at a time

## General information
- Dates are **ISO 8601** format: `YYYY-MM-DD`
- Booleans are lower case: 'true' or 'false'
- Strings are lower case unless otherwise stated
- No field is nullable, if the value is unknown the record is invalid for phase 1

## Student record
### 1.) student_id
- type - string
- required - yes
- allowed values - '0-9', alphanumeric string, underscores

### 2.) today
- type -> date ('YYYY-MM-DD')
- required - yes
- Allowed values - any valid calendar date

### 3.) student_phase
- "enrolled", "opt" or "grace_period"

### 4) enrollment_status
- **Type:** enum (string)
- **Required:** yes
- **Allowed values:**
  - `enrolled`
  - `not_enrolled`
- **Notes:** This is the student’s current enrollment state for the academic term in scope.

### 5) full_time
- **Type:** boolean
- **Required:** yes
- **Allowed values:** `true`, `false`
- **Notes:** Indicates whether the student is currently enrolled at a full-time course load for their program level.

### 6) program_level
- **Type:** enum (string)
- **Required:** yes
- **Allowed values:**
  - `undergraduate`
  - `graduate`
- **Notes:** Phase 1 assumes rules may differ by level.

### 7) program_start_date
- **Type:** date (`YYYY-MM-DD`)
- **Required:** yes
- **Allowed values:** any valid calendar date
- **Constraints:**
  - must be `<= today`
- **Notes:** The start date of the current program (or program instance) being evaluated.

### 8) opt_end_date
- **Type:** date (`YYYY-MM-DD`)
- **Required:** no - only required if student is on opt
- **Allowed values:** any valid calendar date
- **Constraints:**
  - if present, must be `>= program_start_date`
- **Notes:** leave blank or omit entirely for students who have not reached OPT stage. R001 and R003 are skipped automatically when this field is absent.

### 9) sevis_updated

- **Type:** boolean
- **Required:** yes
- **Allowed values:** `true`, `false`
- **Notes:** Whether SEVIS has been updated to reflect the student’s relevant status/changes for the current scenario under evaluation.

---

## Record validity rules (hard failures)
A StudentRecord is **invalid** (Phase 1 must refuse to evaluate) if any of the following are true:
- Any required field is missing
- Any date is not in `YYYY-MM-DD`
- `program_start_date > today`
- `opt_end_date < program_start_date`
- Any enum field is outside allowed values

---

#### example
```json
{
  "student_id": "stu_01928",
  "today": "2026-01-06",
  "enrollment_status": "enrolled",
  "full_time": true,
  "program_level": "graduate",
  "program_start_date": "2025-08-26",
  "opt_end_date": "2026-07-15",
  "sevis_updated": false
}
```

## PHASE 2 
## Purpose 
Phase 2 is an extension of Phase 1 to suppory institutional batch evaluation. A DSO submits a CSV file with multiple student records.
The engine evaluates each row independently using the same Phase 1 rules. 

## CSV requirements
- File format: '.csv' 
- Encoding: UTF-8
- First row- column headers. Must match exact field names
- One student per row
- No blank rows in between 
- maximum batch size - 500 students per file

---

## Batch validity rules
- If a row fails Phase 1 hard failure rules, it is skipped and flagged in the output reports, and processing of the bacth continues.
- The output report identifies every skipped row by student_id and reason for skipping
- A batch with zero valid rows returns an error

## Output per row
Each valid row produces:
- student_id
- overall_status: Red, Yellow or Green
- Triggered rules: a list of rules 
- Recommended action

---


### Example : csv file 
student_id,today,enrollment_status,full_time,program_level,program_start_date,opt_end_date,sevis_updated

stu_01928,2026-01-14,enrolled,true,graduate,2025-08-26,2026-07-15,false

stu_01929,2026-01-14,not_enrolled,false,graduate,2024-08-26,2026-02-28,false

stu_01930,2026-01-14,enrolled,true,undergraduate,2025-09-01,2027-06-01,true


