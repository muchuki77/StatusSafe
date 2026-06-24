-- StatusSafe Phase 3 Database Schema
-- SQLite

CREATE TABLE IF NOT EXISTS batches (
    batch_id      TEXT PRIMARY KEY,
    assessed_by   TEXT,
    assessed_at   TEXT NOT NULL,
    total_records INTEGER,
    red_count     INTEGER,
    yellow_count  INTEGER,
    green_count   INTEGER,
    skipped_count INTEGER
);

CREATE TABLE IF NOT EXISTS assessments (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    batch_id        TEXT NOT NULL,
    student_id      TEXT NOT NULL,
    department      TEXT,
    overall_status  TEXT NOT NULL,
    triggered_rules TEXT,
    assessed_at     TEXT NOT NULL,
    FOREIGN KEY (batch_id) REFERENCES batches(batch_id)
);

CREATE TABLE IF NOT EXISTS rule_triggers (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER NOT NULL,
    student_id    TEXT NOT NULL,
    batch_id      TEXT NOT NULL,
    rule_id       TEXT NOT NULL,
    rule_name     TEXT NOT NULL,
    severity      TEXT NOT NULL,
    triggered_at  TEXT NOT NULL,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);

CREATE TABLE IF NOT EXISTS resolutions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id    TEXT NOT NULL,
    rule_id       TEXT NOT NULL,
    assessment_id INTEGER NOT NULL,
    resolved_by   TEXT,
    resolved_at   TEXT NOT NULL,
    notes         TEXT,
    FOREIGN KEY (assessment_id) REFERENCES assessments(id)
);

-- Analytics queries
-- Most common triggered rule
-- SELECT rule_name, COUNT(*) as frequency
-- FROM rule_triggers
-- GROUP BY rule_name
-- ORDER BY frequency DESC;

-- Repeat alerts
-- SELECT student_id, COUNT(*) as alert_count
-- FROM assessments
-- WHERE overall_status = 'RED'
-- GROUP BY student_id
-- HAVING alert_count > 1
-- ORDER BY alert_count DESC;

-- Department non-compliance rate
-- SELECT department,
--        ROUND(100.0 * SUM(CASE WHEN overall_status != 'GREEN' 
--              THEN 1 ELSE 0 END) / COUNT(*), 1) as rate
-- FROM assessments
-- WHERE department IS NOT NULL
-- GROUP BY department
-- ORDER BY non_compliance_rate DESC;

-- Student flagged but never resolved
-- SELECT DISTINCT a.student_id, a.overall_status, a.assessed_at
-- FROM assessments a
-- LEFT JOIN resolutions r ON a.id = r.assessment_id
-- WHERE a.overall_status = 'RED' AND r.id IS NULL
-- ORDER BY a.assessed_at ASC;

-- Average resolution time per rule
-- SELECT r.rule_id
--      AVG(JULIANDAY(resolved_at) - JULIANDAY(a.assessed_at)) as avg_resolution_time_minutes
-- FROM resolutions r
-- JOIN assessments a ON r.assessment_id = a.id
-- GROUP BY r.rule_id;
-- ORDER BY avg_days_to_resolve DESC;