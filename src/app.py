import streamlit as st
import json
import os
import sys
import sqlite3
from datetime import datetime
import pandas as pd

# Ensure src is on the path
sys.path.insert(0, os.path.dirname(__file__))

from rules_engine import evaluate_rules, process_batch
from database import (
    init_database,
    save_batch_results,
    get_batch_history,
    get_most_common_rules,
    get_repeat_alerts,
    save_resolution,
    get_resolutions
)


# Page config 
st.set_page_config(
    page_title="StatusSafe",
    page_icon="🚦",
    layout="centered"
)

# Sidebar with tool description
st.sidebar.title("🚦 StatusSafe")
st.sidebar.markdown("**What is this?**")
st.sidebar.markdown(
    "A prototype compliance-support tool that flags "
    "potential F-1 status risks before they become legal problems."
)
st.sidebar.markdown("**Who is it for?**")
st.sidebar.markdown(
    "International students, DSOs, and institutional "
    "administrators navigating common transition points."
)
st.sidebar.divider()

st.sidebar.markdown("**📖 How to use**")
st.sidebar.markdown(
    "1. Select the profile that matches your situation\n"
    "2. Click **Run Compliance Check**\n"
    "3. Read your risk result\n"
    "4. Follow the recommended action"
)
st.sidebar.divider()

# Risk level reference
st.sidebar.markdown("**🔔 Risk Levels**")
st.sidebar.markdown("🟢 **Green** — No issues detected")
st.sidebar.markdown("🟡 **Yellow** — Take caution! Review your situation")
st.sidebar.markdown("🔴 **Red** — Critical! Contact your DSO now")

st.sidebar.divider()

st.sidebar.info(
    "💼 **Always contact your DSO**\n\n"
    "This tool helps you know *when* to reach out. "
    "Your Designated School Official (DSO)is your authoritative "
    "source for all immigration decisions."
)

st.sidebar.divider()

st.sidebar.warning(
    "⚠️ ** Disclaimer** \n\n"
    "This tool does not provide legal advice and does "
    "not interact with real SEVIS or student data. "
    "All profiles shown are mock data for illustration "
    "and educational purposes only."
)

st.divider()

# Profile selector 
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
SAMPLES_DIR = os.path.join(PROJECT_ROOT, "samples")

profile_options = {
    "🟢 Low Risk — Fully Compliant":
        "student_green_rule5.json",
    "🟡 Moderate Risk — OPT Grace Period Nearing":
        "student_yellow_rule3.json",
    "🟡 Moderate Risk — Under Enrollment":
        "student_yellow_rule4.json",
    "🔴 High Risk — OPT Ended Without SEVIS Update":
        "student_red_rule1.json",
    "🔴 High Risk — Enrollment Without SEVIS Update":
        "student_red_rule2.json",
    "🔴 High Risk — Precedence Case (Red over Yellow)":
        "student_precedence_red_over_yellow.json",
}

selected_label = st.selectbox(
    "Select a student profile to assess:",
    list(profile_options.keys())
)

# Run assessment 
if st.button("Run Compliance Check", type="primary"):

    filename = profile_options[selected_label]
    path = os.path.join(SAMPLES_DIR, filename)

    with open(path) as f:
        student_data = json.load(f)

    result = evaluate_rules(student_data)
    overall = result["overall_status"]
    rule_results = result["rule_results"]

    st.divider()

    # Overall status banner
    if overall == "RED":
        st.error(f"🔴 Overall Status: HIGH RISK")
    elif overall == "YELLOW":
        st.warning(f"🟡 Overall Status: MODERATE RISK")
    else:
        st.success(f"🟢 Overall Status: LOW RISK — Fully Compliant")

    st.divider()

    # Student profile
    with st.expander("📋 Student Profile", expanded=False):
        st.json(student_data)

    # Triggered rules
    triggered = [r for r in rule_results if r["status"] == "Triggered"]
    passing = [r for r in rule_results if r["status"] == "Pass"]

    if triggered:
        st.subheader("⚠️ Triggered Rules")
        for rule in triggered:
            if rule["severity"] == "Critical":
                color = "🔴"
            else:
                color = "🟡"

            with st.expander(
                f"{color} [{rule['rule_id']}] {rule['name']}",
                expanded=True
            ):
                st.markdown(f"**Severity:** {rule['severity']}")
                st.markdown(f"**Issue:** {rule['message']}")
                st.markdown(
                    f"**Recommended Action:** {rule['recommended_action']}"
                )
                st.markdown("**Evidence:**")
                for key, value in rule["evidence"].items():
                    st.markdown(f"- `{key}`: {value}")

    # Passing rules
    with st.expander("✅ Passing Rules", expanded=False):
        for rule in passing:
            st.markdown(f"- [{rule['rule_id']}] {rule['name']}")

    st.divider()
    st.caption(
        "⚠️ This tool does not provide legal advice. "
        "All data is mock data for demonstration purposes only."
    )


st.divider()

st.subheader("Check My own Status")
st.markdown("Enter your own student information to assess your F-1 status compliance.")

with st.form("student compliance form"):

        col1, col2 = st.columns(2)

        with col1:
            today       = st.date_input("Today's date")
            enroll      = st.selectbox(
                            "Enrollment status",
                            ["enrolled", "not_enrolled"]
                        )
            full_time   = st.checkbox("I am enrolled full time")
            level       = st.selectbox(
                            "Program level",
                            ["graduate", "undergraduate"]
                        )

        with col2:
            start_date  = st.date_input("Program start date")
            on_opt      = st.checkbox("I am currently on OPT")
            opt_end     = st.date_input(
                            "OPT end date",
                            value=None,
                            disabled=not on_opt
                        ) if on_opt else None
            sevis       = st.checkbox("My SEVIS record has been updated")

        submitted = st.form_submit_button(
            "Check My Status",
            type="primary"
        )

if submitted:
    # Build student data dictionary from inputs
    student_data = {
        "student_id": "self_check",
        "today": today.isoformat(),
        "enrollment_status": enroll,
        "full_time": full_time,
        "program_level": level,
        "program_start_date": start_date.isoformat(),
        "opt_end_date": opt_end.isoformat() if opt_end else "",
        "sevis_updated": sevis
    }

    result = evaluate_rules(student_data)
    overall = result["overall_status"]
    rules = result["rule_results"]

    st.divider()

     # Overall status banner
    if overall == "RED":
        st.error(f"🔴 Overall Status: HIGH RISK - Contact your DSO as soon as possible")
    elif overall == "YELLOW":
        st.warning(f"🟡 Overall Status: MODERATE RISK - Review your situation and contact your DSO if necessary")
    else:
        st.success(f"🟢 Overall Status: LOW RISK — Fully Compliant")
    
    # Triggered rules
    triggered = [r for r in rules if r["status"] == "Triggered"]

    if triggered:
        st.subheader("⚠️ Issues Found")
        for rule in triggered:
            icon = "🔴" if rule["severity"] == "Critical" else "🟡"
            with st.expander(
                f"{icon} {rule['name']}",
                expanded=True
            ):
                st.markdown(f"**Issue:** {rule['message']}")
                st.markdown(
                    f"**Recommended Action:** {rule['recommended_action']}"
                )
    else:
        st.info("✅ No issues detected. Your F-1 status appears compliant.")

    st.caption(
        "⚠️ This tool does not provide legal advice. "
        "Always confirm with your DSO before making "
        "any immigration decisions."
    )

st.divider()

st.subheader("📂 Batch Assessment — Upload Student Records")
st.markdown(
    "For institutional use, upload a CSV file containing multiple student records to assess compliance in bulk")


uploaded_file = st.file_uploader(
    "Upload CSV file",
    type="csv",
    help="CSV must follow the StatusSafe data schema. "
         "See docs/data_schema.md for field requirements."
)
if uploaded_file is not None:
    import pandas as pd
    import io
    # Read csv 
    df = pd.read_csv(uploaded_file)
    st.markdown(f"**{len(df)} student record loaded.**")
    # preview the uploaded data
    with st.expander("📋 preview uploaded data", expanded=False):
        st.dataframe(df)
    if st.button("Run Batch Assessment", type = "primary"):
        # convert dataframe rows to list of dictionaries for each student
        rows = df.to_dict(orient="records")
        output = process_batch(rows) # defined in rules_engine.py   

        from database import init_database, save_batch_results
        init_database() # ensure database is initialised
        batch_id = save_batch_results(output, assessed_by="DSO") # save results to database

        st.session_state["batch_output"] = output
        st.session_state["batch_df"] = pd.DataFrame([])
        st.session_state["batch_id"] = batch_id # batch id stored in session state for reference


        # store in-session so results persists
        st.session_state["batch_output"] = output
        st.session_state["batch_df"]     = pd.DataFrame([
            {
                "Student ID":       r["student_id"],
                "Status":           r["rule_evaluation"]["overall_status"],
                "Issues Found":     "\n".join([
                                        x["name"] for x in
                                        r["rule_evaluation"]["rule_results"]
                                        if x["status"] == "Triggered"
                                    ]) or "None",
                "Actions Required": "\n".join([
                                        x["recommended_action"] for x in
                                        r["rule_evaluation"]["rule_results"]
                                        if x["status"] == "Triggered"
                                    ]) or "None"
            }
            for r in output["results"]
    ])
    # Display results outside button block so it shows after assessment is run/after download button is clicked.
if "batch_output" in st.session_state:
    # process batch
    output = st.session_state["batch_output"]
    summary = output["summary"]
    results = output["results"]
    skipped = output["skipped"]
    display_df = st.session_state["batch_df"]

    st.divider()
    st.subheader("📊 Batch Summary")

    # Timestamp
    st.caption(
        f"Batch processed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    # lets let the DSO know that tthe assessment results have been saved to the database
    if "batch_id" in st.session_state:
        st.caption(
            f"Assessment ID: {st.session_state['batch_id']} — results saved to database"
        )
    # Colour coded metrics
    total     = summary["total_evaluated"]
    red_count = summary["red"]
    yel_count = summary["yellow"]
    grn_count = summary["green"]

    st.markdown(f"""
    <div style="display: flex; gap: 16px; margin: 16px 0;">
        <div style="flex:1; background:#f8f9fa; border-left: 6px solid #6c757d;
                    padding: 16px; border-radius: 8px; text-align: center;">
            <div style="font-size: 2.2em; font-weight: bold;
                        color: #2c3e50;">{total}</div>
            <div style="font-size: 0.9em; color: #666;">Total Evaluated</div>
        </div>
        <div style="flex:1; background:#fff5f5; border-left: 6px solid #e74c3c;
                    padding: 16px; border-radius: 8px; text-align: center;">
            <div style="font-size: 2.2em; font-weight: bold;
                        color: #e74c3c;">{red_count}</div>
            <div style="font-size: 0.9em; color: #666;">🔴 High Risk</div>
        </div>
        <div style="flex:1; background:#fffbf0; border-left: 6px solid #f39c12;
                    padding: 16px; border-radius: 8px; text-align: center;">
            <div style="font-size: 2.2em; font-weight: bold;
                        color: #f39c12;">{yel_count}</div>
            <div style="font-size: 0.9em; color: #666;">🟡 Moderate Risk</div>
        </div>
        <div style="flex:1; background:#f0fff4; border-left: 6px solid #27ae60;
                    padding: 16px; border-radius: 8px; text-align: center;">
            <div style="font-size: 2.2em; font-weight: bold;
                        color: #27ae60;">{grn_count}</div>
            <div style="font-size: 0.9em; color: #666;">🟢 Compliant</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Split bar
    if total > 0:
        compliant_bar     = round((grn_count / total) * 100)
        non_compliant_bar = 100 - compliant_bar

        st.markdown(f"""
        <div style="margin: 8px 0 4px 0;">
            <div style="display: flex; justify-content: space-between;
                        font-size: 0.85em; color: #666; margin-bottom: 4px;">
                <span>🟢 Compliant {compliant_bar}%</span>
                <span>🔴 Non-Compliant {non_compliant_bar}%</span>
            </div>
            <div style="display: flex; height: 20px; border-radius: 10px;
                        overflow: hidden; background: #eee;">
                <div style="width: {compliant_bar}%; 
                            background: #27ae60;"></div>
                <div style="width: {non_compliant_bar}%; 
                            background: #e74c3c;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    if summary["skipped"] > 0:
        st.warning(
            f"⚠️ {summary['skipped']} records skipped "
            f"due to validation errors."
        )

    # Results table
    st.subheader("📋 Student Results")
    st.dataframe(display_df)

    st.download_button(
        label="📥 Download Results as CSV",
        data=display_df.to_csv(index=False),
        file_name="statussafe_batch_results.csv",
        mime="text/csv"
    )

    if skipped:
        with st.expander(
            f"⚠️ Skipped Records ({len(skipped)})",
            expanded=False
        ):
            for s in skipped:
                st.markdown(
                    f"- **{s['student_id']}** — {s['validation_reason']}"
                )

    st.caption(
        "⚠️ This tool does not provide legal advice. "
        "All results are for demonstration purposes only."
    )

# add an analytics section to the app to show batch history, most common rules, and repeat alerts        
st.divider()
st.subheader("📊 Compliance Analytics")
st.markdown("Historical compliance data from previous batch assessments.")

history = get_batch_history()
common_rules = get_most_common_rules()
repeats = get_repeat_alerts()

if not history:
    st.info(
        "No batch history found. Run a batch assessment to generate "
        "compliance data."
    )
else:
    # batch history
    st.markdown("**📋 Assessment History**")
    history_df = pd.DataFrame(history)
    history_df = history_df.rename(columns={
        "batch_id":      "Batch ID",
        "assessed_by":   "Assessed By",
        "assessed_at":   "Date",
        "total_records": "Total",
        "red_count":     "🔴 RED",
        "yellow_count":  "🟡 YELLOW",
        "green_count":   "🟢 GREEN",
        "skipped_count": "Skipped"
    })
    resolutions = get_resolutions()
    if resolutions:
        resolutions_df = pd.DataFrame(resolutions)
        resolutions_df = resolutions_df.rename(columns={
            "student_id":    "Student ID",
            "rule_id":       "Rule ID",
            "assessment_id": "Assessment ID",
            "resolved_by":   "Resolved By",
            "resolved_at":   "Resolved At",
            "notes":         "Notes",
            "overall_status": "Status", 
            "batch_id":      "Batch ID"
        })
        
        st.dataframe(resolutions_df[["Student ID", "Rule ID", "Assessment ID", "Resolved By", "Resolved At", "Notes", "Status", "Batch ID"]])
    else:
        st.info("No resolutions found. Students flagged in previous batches have not been marked as resolved.")


st.divider()
if  common_rules:
    st.markdown("**⚠️ Most Triggered Rules**")
    rules_df = pd.DataFrame(common_rules)
    rules_df = rules_df.rename(columns={
        "rule_id":    "Rule ID",
        "rule_name":  "Rule Name",
        "frequency":  "Times Triggered"
    })
    st.dataframe(rules_df)
st.divider()

# repeat alerts
st.markdown("**🔁 Repeat Alerts; Students flagged multiple times**")
if repeats:
    repeats_df = pd.DataFrame(repeats)
    repeats_df = repeats_df.rename(columns={
        "student_id":  "Student ID",
        "alert_count": "Times Flagged",
        "last_flagged": "Last Flagged Date"
    })
    st.dataframe(repeats_df)

# resolution form
st.markdown("✅ Mark student as resolved")
st.markdown("Use this form to mark a student as resolved, which will remove them from the repeat alerts list.")
with st.form("resolution_form"):
        col1, col2 = st.columns(2)

        with col1:
            student_options = [
                r["student_id"] for r in repeats
            ]
            selected_student = st.selectbox(
                "Student ID",
                student_options
            )
            rule_options = ["R001", "R002", "R003", "R004"]
            selected_rule = st.selectbox(
                "Rule resolved",
                rule_options
            )

        with col2:
            resolved_by = st.text_input(
                "Your name or DSO ID",
                placeholder="e.g. DSO_Jane"
            )
            notes = st.text_area(
                "Action taken",
                placeholder="e.g. Student contacted, SEVIS updated on 2026-07-05",
                height=100
            )

        resolve_submitted = st.form_submit_button(
            "Mark as Resolved",
            type="primary"
        )

if resolve_submitted:
        if not resolved_by.strip():
            st.error("Please enter your name or DSO ID.")
        elif not notes.strip():
            st.error("Please describe the action taken.")
        else:
            # Get the assessment_id for this student
            conn_temp = sqlite3.connect(
                os.path.join(
                    os.path.dirname(__file__),
                    '..', 'data', 'statussafe.db'
                )
            )
            cursor_temp = conn_temp.cursor()
            cursor_temp.execute("""
                SELECT id FROM assessments
                WHERE student_id = ?
                AND overall_status = 'RED'
                ORDER BY assessed_at DESC
                LIMIT 1
            """, (selected_student,))
            row = cursor_temp.fetchone()
            conn_temp.close()

            if row:
                success = save_resolution(
                    student_id=selected_student,
                    rule_id=selected_rule,
                    assessment_id=row[0],
                    resolved_by=resolved_by.strip(),
                    notes=notes.strip()
                )
                if success:
                    st.success(
                        f"✅ {selected_student} marked as resolved. "
                        f"They will be removed from repeat alerts."
                    )
                    st.rerun()
                else:
                    st.error("Failed to save resolution. Try again.")
            else:
                st.error("Could not find assessment record for this student.")

else:
    st.info(
        "✅ No repeat alerts found. " 
        "No students have been flagged RED more than once."
    )
st.caption("Analytics update automatically after each batch assessment.")

    
# 


