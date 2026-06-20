# StatusSafe Phase 2 — Scope Document

## Status: Complete — June 2026

---

## Goal

Extend StatusSafe from a single-student demonstration tool into an institutional compliance assessment system capable of processing batch student records.

---

## Completed — Month 1

- [x] CSV schema defined — docs/data_schema.md updated
- [x] validate_csv_row() built and tested
- [x] opt_end_date made optional for non-OPT students
- [x] R001 and R003 guards added
- [x] CSV file upload in Streamlit
- [x] process_batch() built and connected to interface
- [x] Batch results display — summary metrics and table
- [x] Seven sample profiles verified

## Completed — Month 2

- [x] Visual batch summary — colour coded metric cards
- [x] Split compliance and non-compliance progress bar
- [x] Timestamp on every assessment
- [x] Results table — full rule names and recommended actions
- [x] Results sorted by risk level
- [x] Export button — download results as CSV
- [x] Persistent results using session state
- [x] Individual student self-check form

## Completed — Month 3

- [x] Input validation hardening
- [x] Future today date rejected
- [x] Case insensitive field normalisation
- [x] NaN opt_end_date handled gracefully
- [x] Edge case test suite — 17 tests all passing
- [x] ASSUMPTIONS.md updated — ten year cutoff removed
- [x] README updated with Phase 2 features and screenshot
- [x] DSO User Guide written
- [x] CHANGELOG updated
- [x] PHASE2_SCOPE marked complete

## Deferred to Phase 3

- [ ] Persistent storage across sessions
- [ ] Resolution tracking workflow
- [ ] Process metrics dashboard
- [ ] Department level analytics
- [ ] Student name and email optional fields

## Deferred to Phase 4

- [ ] Synthetic data generation
- [ ] ML risk scoring model
- [ ] Probability score in interface
- [ ] Predictive compliance risk

---

## Notes

Had placed an initial program start date cutoff but removed after review because of no regulatory basis for justificaton.

Phase 2 was completed ahead of the original four month schedule. Months 1 and 2 were completed in the first two sessions. Month 3 edge case testing and documentation
completed in subsequent sessions.