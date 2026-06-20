# Changelog

All notable changes to StatusSafe are documented here.

---

## Phase 2 — June 2026

### Added
- CSV batch upload for institutional use — maximum 500 records
- Input validation layer — all eight required fields checked before processing
- Boolean normalisation — handles pandas true/false types
- String normalisation — case insensitive enrollment status and program level
- NaN handling — empty opt_end_date treated as absent
- Batch processing engine — invalid rows skipped gracefully without stopping the batch
- Visual batch summary dashboard — colour coded metric cards
- Split compliance and non-compliance progress bar
- Timestamp on every batch assessment
- Results table with full rule names and recommended actions
- Results sorted by risk level — RED first, YELLOW, GREEN last
- Download batch results as CSV
- Persistent results using session state
- Individual student self-check form — Check My Own Status
- Edge case test suite — 17 tests all passing
- Expanded data schema documentation for Phase 2 CSV format
- DSO User Guide — docs/DSO_USER_GUIDE.md
- Dashboard screenshot added to README

### Fixed
- opt_end_date made optional — students not on OPT no longer rejected
- R001 and R003 guards added — rules skipped gracefully when opt_end_date is absent
- R003 guard rule_id corrected from R001 to R003
- Double append bug resolved in process_batch()
- Boolean type assumption bug fixed — handles both string and bool types from pandas

### Known Limitations
- No persistent storage across sessions — results lost on page refresh
- Mock data only. Does not connect to real SEVIS system
- No resolution tracking — no way to mark issues as resolved
- No department level analytics — planned for Phase 3

---

## Phase 1 — May 2026

### Added
- Rules engine with five F-1 compliance rules
  - R001 OPT ended without SEVIS update — Critical
  - R002 Enrollment without SEVIS program extension — Critical
  - R003 OPT grace period nearing expiration — Warning
  - R004 Under-enrollment while on F-1 — Warning
  - R005 No issues detected — Info
- Severity precedence — Critical overrides Warning
- Seven sample profiles covering all risk scenarios
- Verified test suite — all seven samples passing
- Terminal compliance report with formatted output
- Streamlit web interface with sidebar navigation
- Single profile selector with mock student scenarios
- Deployed live at statussafe.streamlit.app
- MIT License added
- README with project description and live demo link

---

## Planned — Phase 3

- Persistent storage layer — SQLite database
- Assessment history tracking across sessions
- Resolution tracking — mark issues as resolved
- Process metrics — average resolution time, most common issues, repeat alerts
- Department level non-compliance analytics
- Optional student name and email fields for DSO workflow
- Urgency indicators for RED students — days since expiry

## Planned — Phase 4

- Synthetic data generation using rules engine as labeler
- ML risk scoring model — logistic regression baseline
- Probability score alongside rule-based results
- Predictive compliance risk from historical patterns
