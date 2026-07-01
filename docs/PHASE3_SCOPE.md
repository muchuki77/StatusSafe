# StatusSafe Phase 3 — Intelligent Compliance Ecosystem

## StatusSafe Phase 4 - Planned

## Goal
Transform StatusSafe from a point-in-time detector into an institutional compliance management system with memory, analytics, and predictive intelligence.

**Phase 2 tells you whats currently wrong while Phase 3 tells you whats been wrong, how wrong and what is likely to go wrong**

## Process Metrics
- Average resolution time per rule type: Time a DSO takes to resolve a RED flag
- Most common triggered rules across cohorts: What compliance gaps appear most frequently?
- Repeat alert tracking per student: Which students are flagged repeatedly without resolution?
- Department-level non-compliance rates: Which departments or programs haave the highest risk been flagged?
- Seasonal pattern:When do compliance risks spike? mid-semester?, during transitions?

## Technical Requirements
- SQLite persistent storage layer
Two core tables:
**assesment** - batch and individual assesment stored
```sql
CREATE TABLE assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id        TEXT,
    student_id      TEXT,
    department      TEXT,
    overall_status  TEXT,
    triggered_rules TEXT,
    assessed_at     TEXT
);
```

**resolutions** - DSO marks issues as resolved
```sql
CREATE TABLE resolutions (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   TEXT,
    rule_id      TEXT,
    resolved_date  TEXT,
    resolved_by  TEXT,
    notes        TEXT
);
```

- Resolution tracking workflow
    - DSO can mark an issue as resolved with notes
    - DSO can mark a flagged student as contacted
    - System records time stamp for every resolution
    - Resolved student are removed from active alert list

- Department field in data schema
    - Add optional 'department' field to data shemma
    student_id, today, enrollment_status, full_time, program_level, program_start_date, opt_end_date, sevis_updated, department
    - Enables filtering by department in the anlystics dashboard

- Historical assessment aggregation
    - Store every assesment result with timestamp. how about individual student?
    - Query across time to identify patterns
    - Compare currrnt batch across historical baseline
    - Flag students who's status has not improved

## ML Intelligence Layer
- Predictive risk scoring from historical patterns
    Train a logistic regression model, on historical assesment data to predict compliance risk before rule fires
    Input features:
        - Days until opt end date
        - Enrollment status
        - Program level
        - Days since program start
        - Historical alert count for this student
        - Department non-compliance rate
    Output:
        - Risk probability score (0.0 to 1.0)
        - Shown alongside rule-based RED/YELLOW/GREEN result


- Early warning for students approaching compliance risk
    Flags student approaching compliance risk before a rule triggers For example a student whose OPT ends in 90 days with FALSE sevis_updated is not yet red but is trending towards it.

- Institutional pattern detection
    Identify departments, program transitions or time periods that consistentlyproduce high non-compliance rates. Surface these patterns to DSO's

- Longitudinal compliance trajectory modelling
    Track each student's assesments over time. Foe example a student who has been at YELLOW three times in a row is at higher risk than a first time YELLOW ven if current rules do not capture this.

---- 

New features for the interface
    - Historical dashboard: compalliance tredns over time
    - Student timeline: view a student's full assesment history
    - Resolution tracker: mark issues as resolved and track progress
    - Department analytics: filter results by department 
    - Early warning list: students approaching risk before rule fires
    - ML risk score: probability risk score alongside rule results

## Schema Changes Required

```markdown
| Field      | Type   | Required | Notes                    |
|------------|--------|----------|--------------------------|
| department | string | No       | New in Phase 3           |
| batch_id   | string | No       | Groups batch assessments |
```

## Open Questions For Institutional Partners

- Does your institution sponsor postdoctoral F-1 students?
  If so, should program_level include a postdoctoral option?
- What is your typical resolution workflow after a DSO
  identifies a compliance risk?
- Which departments or transitions produce the most
  compliance issues at your institution?
- What data can you share for model training while
  maintaining student privacy?


## Dependencies

Phase 3 ML intelligence layer requires completion of:
- Gradient descent and optimisation — Hartmann Chapter 15
- Classical ML algorithms — logistic regression, Month 2
- Model evaluation — precision, recall, AUC-ROC
- Feature engineering for compliance data

**Timeline: Month 4 — after ML foundations are complete**

## Notes

The synthetic data generation strategy uses the existing rules engine as a labeler — generate student profiles, run them through the rules engine, use the output as training labels. This avoids the need for real student data while producing a realistic training set.

See docs/ASSUMPTIONS.md for open questions on postdoctoral F-1 students and department field design.
