## Purpose
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
- allowed values - '0-9'

### 2.) Today
- type -> date ('YYYY-MM-DD')
- required - yes
- Allowed values - any valid calendar date

### 3) enrollment_status
- **Type:** enum (string)
- **Required:** yes
- **Allowed values:**
  - `enrolled`
  - `not_enrolled`
- **Notes:** This is the student’s current enrollment state for the academic term in scope.

### 4) full_time
- **Type:** boolean
- **Required:** yes
- **Allowed values:** `true`, `false`
- **Notes:** Indicates whether the student is currently enrolled at a full-time course load for their program level.

### 5) program_level
- **Type:** enum (string)
- **Required:** yes
- **Allowed values:**
  - `undergraduate`
  - `graduate`
- **Notes:** Phase 1 assumes rules may differ by level.

### 6) program_start_date
- **Type:** date (`YYYY-MM-DD`)
- **Required:** yes
- **Allowed values:** any valid calendar date
- **Constraints:**
  - must be `<= today`
- **Notes:** The start date of the current program (or program instance) being evaluated.

### 7) opt_end_date
- **Type:** date (`YYYY-MM-DD`)
- **Required:** yes
- **Allowed values:** any valid calendar date
- **Constraints:**
  - must be `>= program_start_date`
- **Notes:** For Phase 1, this is treated as a known date used for “time-to-OPT-end” checks. If OPT does not apply, do not pass a record into Phase 1 evaluation (Phase 1 is strict).

### 8) sevis_updated
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

### example
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

