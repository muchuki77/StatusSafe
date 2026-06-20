# StatusSafe - DSO User Guide

**For Designated School Officials  and Institutional Administrators**

---

## What Is StatusSafe?

StatusSafe is a compliance-support tool that helps identify potential F-1 status risks before they become legal problems. 
It flags gaps during common student transitions such as OPT end dates, enrollment changes, and SEVIS update alignment.

**What StatusSafe is:**
- An early warning and decision-support tool
- A way to identify which students may need follow-up
- A demonstration prototype built on known F-1 compliance rules

**What StatusSafe is not:**
- A legal advice tool
- A replacement for your DSO judgment or institutional process
- Connected to real SEVIS data or any government system

---

## How To Use The Batch Assessment

### Step 1 — Prepare Your CSV File

Create a CSV file with one row per student. 
The file must include these column headers exactly:

student_id, today, enrollment_status, full_time, program_level, program_start_date, opt_end_date, sevis_updated

**Field reference:**

| Field | Accepted Values | Required |
|---|---|---|
| student_id | Any alphanumeric ID | Yes |
| today | YYYY-MM-DD | Yes |
| enrollment_status | enrolled, not_enrolled | Yes |
| full_time | true, false | Yes |
| program_level | graduate, undergraduate | Yes |
| program_start_date | YYYY-MM-DD | Yes |
| opt_end_date | YYYY-MM-DD | No — leave blank if not on OPT |
| sevis_updated | true, false | Yes |

**Example row:** stu_001, 2026-01-14, enrolled, true, graduate, 2025-08-26, 2026-07-15, false

---

### Step 2 — Upload and Run

1. Go to [statussafe.streamlit.app](https://statussafe.streamlit.app)
2. Scroll to **Batch Assessment — Upload Student Records**
3. Click **Browse Files** and select your CSV
4. Review the preview table to confirm records loaded correctly
5. Click **Run Batch Assessment**

---

### Step 3 — Read The Results

**Batch Summary Dashboard**

The dashboard shows four metrics at a glance:
- Total students evaluated
- High Risk count — RED
- Moderate Risk count — YELLOW
- Compliant count — GREEN

The split bar shows the compliance rate visually: green for compliant, red for non-compliant.

**Results Table**

Each student row shows:
- Student ID
- Overall risk status
- Issues Found — the specific rule that triggered
- Actions Required — what to do next

Results are sorted RED first so the most urgent 
cases appear at the top.

---

### Step 4 — Interpret The Risk Levels

**🔴 RED — High Risk**
A critical compliance issue was detected. The student's record shows a condition that may indicate an F-1 status violation. 
Contact this student as soon as possible to review their SEVIS record and confirm their status.

**🟡 YELLOW — Moderate Risk**
A potential compliance issue was detected that requires attention before it escalates. 
Review the student's situation and confirm whether corrective action is needed.

**🟢 GREEN — Compliant**
No compliance issues detected based on the information provided. 

No immediate action required.

---

### Step 5 — Download and Act

Click **Download Results as CSV** to save the full report.
The downloaded file includes:
- Student ID
- Risk status
- Issues found — full rule names
- Actions required — specific recommended steps

Use this file to prioritise follow-up with students flagged as RED or YELLOW.

---

## How To Use The Individual Student Check

Students can check their own status using the 
**Check My Own Status** form:

1. Enter today's date
2. Select enrollment status
3. Check full time enrollment if applicable
4. Select program level
5. Enter program start date
6. Check OPT box and enter OPT end date if applicable
7. Check SEVIS updated if applicable
8. Click **Check My Status**

The tool will return an immediate risk assessment with specific issues and recommended actions if any are found.

---

## Important Limitations

- This tool uses rules based on general F-1 compliance guidance. It does not account for individual student circumstances or exceptions authorised by your institution.
- The tool is only as accurate as the data provided. Incorrect or incomplete records will produce unreliable results.
- A GREEN result does not guarantee full compliance. Always verify with your institution's records.
- This tool does not replace a formal SEVIS review or legal immigration advice.

---

## Disclaimer

StatusSafe does not provide legal advice and does not interact with real SEVIS or student data. All results are for decision-support purposes only. Always confirm 
findings with your institution's official records and consult qualified immigration counsel when appropriate.

---

## Questions or Feedback

This is a prototype project. For questions or feedback contact the author via GitHub:
[github.com/muchuki77/StatusSafe](https://github.com/muchuki77/StatusSafe)


