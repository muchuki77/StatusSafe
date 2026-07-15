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

st.title("🚦 StatusSafe ")
st.markdown("F-1 compliance risk assessment tool."
            "Select a tab to get started.")

st.divider()


tab1, tab2, tab3, tab4 = st.tabs([
    "🔎 Student Check",
    "📂 Batch Assessment",
    "📊 Analytics",
    "✅ Resolution Tracking"
])  


## TAB 1 -> STUDENT CHECK
with tab1:

    st.subheader("Check a student profile")
    st.markdown(
        "Select a mock profile to see how StatusSafe "
        "assesses F-1 compliance risk."
    )

    selected_label = st.selectbox(
        "Select a student profile:",
        list(profile_options.keys()) # type: ignore
    )

    if st.button("Run compliance check", type="primary"):
        filename = profile_options[selected_label]
        path = os.path.join(SAMPLES_DIR, filename)

        with open(path) as f:
            student_data = json.load(f)

        result      = evaluate_rules(student_data)
        overall     = result["overall_status"]
        rule_results = result["rule_results"]

        st.divider()
 
        if overall == "RED":
            st.error("🔴 Overall status: HIGH RISK")
        elif overall == "YELLOW":
            st.warning("🟡 Overall status: MODERATE RISK")
        else:
            st.success("🟢 Overall status: LOW RISK — Fully compliant")

        with st.expander("📋 Student profile", expanded=False):
            st.json(student_data)

        triggered = [r for r in rule_results if r["status"] == "Triggered"]
        passing   = [r for r in rule_results if r["status"] == "Pass"]

        if triggered:
            st.subheader("⚠️ Triggered rules")
            for rule in triggered:
                color = "🔴" if rule["severity"] == "Critical" else "🟡"
                with st.expander(
                    f"{color} [{rule['rule_id']}] {rule['name']}",
                    expanded=True
                ):
                    st.markdown(f"**Severity:** {rule['severity']}")
                    st.markdown(f"**Issue:** {rule['message']}")
                    st.markdown(
                        f"**Recommended action:** {rule['recommended_action']}"
                    )
                    st.markdown("**Evidence:**")
                    for key, value in rule["evidence"].items():
                        st.markdown(f"- `{key}`: {value}")

        with st.expander("✅ Passing rules", expanded=False):
            for rule in passing:
                st.markdown(f"- [{rule['rule_id']}] {rule['name']}")

        st.caption(
            "⚠️ This tool does not provide legal advice. "
            "All data is mock data for demonstration purposes only."
        )

    st.divider()
    st.subheader("🎓 Check my own status")
    st.markdown(
        "Enter your own details to get an instant "
        "F-1 compliance assessment."
    )

    with st.form("student_compliance_form"):
        col1, col2 = st.columns(2)

        with col1:
            today     = st.date_input("Today's date")
            enroll    = st.selectbox(
                "Enrollment status",
                ["enrolled", "not_enrolled"]
            )
            full_time = st.checkbox("I am enrolled full time")
            level     = st.selectbox(
                "Program level",
                ["graduate", "undergraduate"]
            )

        with col2:
            start_date = st.date_input("Program start date")
            on_opt     = st.checkbox("I am currently on OPT")
            opt_end    = st.date_input(
                "OPT end date",
                value=None,
                disabled=not on_opt
            ) if on_opt else None
            sevis      = st.checkbox("My SEVIS record has been updated")

        submitted = st.form_submit_button(
            "Check my status",
            type="primary"
        )

    if submitted:
        student_data = {
            "student_id":         "self_check",
            "today":              today.isoformat(),
            "enrollment_status":  enroll,
            "full_time":          full_time,
            "program_level":      level,
            "program_start_date": start_date.isoformat(),
            "opt_end_date":       opt_end.isoformat() if opt_end else "",
            "sevis_updated":      sevis
        }

        result  = evaluate_rules(student_data)
        overall = result["overall_status"]
        rules   = result["rule_results"]

        st.divider()

        if overall == "RED":
            st.error(
                "🔴 HIGH RISK — Contact your DSO as soon as possible."
            )
        elif overall == "YELLOW":
            st.warning(
                "🟡 MODERATE RISK — Review your situation and consider contacting your DSO."
                
            )
        else:
            st.success("🟢 LOW RISK — No compliance issues detected.")

        triggered = [r for r in rules if r["status"] == "Triggered"]

        if triggered:
            st.subheader("⚠️ Issues found")
            for rule in triggered:
                icon = "🔴" if rule["severity"] == "Critical" else "🟡"
                with st.expander(
                    f"{icon} {rule['name']}",
                    expanded=True
                ):
                    st.markdown(f"**Issue:** {rule['message']}")
                    st.markdown(
                        f"**Recommended action:** "
                        f"{rule['recommended_action']}"
                    )
        else:
            st.info(
                "✅ No issues detected. "
                "Your F-1 status appears compliant."
            )

        st.caption(
            "⚠️ This tool does not provide legal advice. "
            "Always confirm with your DSO before making "
            "any immigration decisions."
        )
## TAB 2 -> BATCH ASSESSMENT
with tab2:
    st.subheader("📂 Batch Assessment" )
    st.markdown("For institutional use. Upload a CSV file containing up to 500 student records  to assess compliance in bulk")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type="csv",
        help="CSV must follow the StatusSafe data schema. "
             "See docs/data_schema.md for field requirements."
    )

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.markdown(f"**{len(df)} student records loaded.**")

        with st.expander("📋 Preview uploaded data", expanded=False):
            st.dataframe(df)

        if st.button("Run batch assessment", type="primary"):
            rows   = df.to_dict(orient="records")
            output = process_batch(rows)

            init_database()
            batch_id = save_batch_results(
                output, assessed_by="DSO"
            )

            st.session_state["batch_output"] = output
            st.session_state["batch_df"] = pd.DataFrame([
                {
                    "Student ID":       r["student_id"],
                    "Status":           r["rule_evaluation"]["overall_status"],
                    "Issues found":     "\n".join([
                        x["name"] for x in
                        r["rule_evaluation"]["rule_results"]
                        if x["status"] == "Triggered"
                    ]) or "None",
                    "Actions required": "\n".join([
                        x["recommended_action"] for x in
                        r["rule_evaluation"]["rule_results"]
                        if x["status"] == "Triggered"
                    ]) or "None"
                }
                for r in output["results"]
            ])
            st.session_state["batch_id"] = batch_id
    if "batch_output" in st.session_state:
        output     = st.session_state["batch_output"]
        summary    = output["summary"]
        skipped    = output["skipped"]
        display_df = st.session_state["batch_df"]

        st.divider()
        st.subheader("📊 Batch summary")
        st.caption(
            f"Batch processed on: "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if "batch_id" in st.session_state:
            st.caption(
                f"Assessment ID: {st.session_state['batch_id']} "
                f"— results saved to database"
            )

        total     = summary["total_evaluated"]
        red_count = summary["red"]
        yel_count = summary["yellow"]
        grn_count = summary["green"]

        st.markdown(f"""
<div style="display:flex;gap:16px;margin:16px 0;">
    <div style="flex:1;background:#f8f9fa;border-left:6px solid #6c757d;
                padding:16px;border-radius:8px;text-align:center;">
        <div style="font-size:2.2em;font-weight:bold;
                    color:#2c3e50;">{total}</div>
        <div style="font-size:0.9em;color:#666;">Total evaluated</div>
    </div>
    <div style="flex:1;background:#fff5f5;border-left:6px solid #e74c3c;
                padding:16px;border-radius:8px;text-align:center;">
        <div style="font-size:2.2em;font-weight:bold;
                    color:#e74c3c;">{red_count}</div>
        <div style="font-size:0.9em;color:#666;">🔴 High risk</div>
    </div>
    <div style="flex:1;background:#fffbf0;border-left:6px solid #f39c12;
                padding:16px;border-radius:8px;text-align:center;">
        <div style="font-size:2.2em;font-weight:bold;
                    color:#f39c12;">{yel_count}</div>
        <div style="font-size:0.9em;color:#666;">🟡 Moderate risk</div>
    </div>
    <div style="flex:1;background:#f0fff4;border-left:6px solid #27ae60;
                padding:16px;border-radius:8px;text-align:center;">
        <div style="font-size:2.2em;font-weight:bold;
                    color:#27ae60;">{grn_count}</div>
        <div style="font-size:0.9em;color:#666;">🟢 Compliant</div>
    </div>
</div>
        """, unsafe_allow_html=True)

        if total > 0:
            compliant_bar     = round((grn_count / total) * 100)
            non_compliant_bar = 100 - compliant_bar
            st.markdown(f"""
<div style="margin:8px 0 4px 0;">
    <div style="display:flex;justify-content:space-between;
                font-size:0.85em;color:#666;margin-bottom:4px;">
        <span>🟢 Compliant {compliant_bar}%</span>
        <span>🔴 Non-compliant {non_compliant_bar}%</span>
    </div>
    <div style="display:flex;height:20px;border-radius:10px;
                overflow:hidden;background:#eee;">
        <div style="width:{compliant_bar}%;background:#27ae60;"></div>
        <div style="width:{non_compliant_bar}%;background:#e74c3c;"></div>
    </div>
</div>
            """, unsafe_allow_html=True)

        if summary["skipped"] > 0:
            st.warning(
                f"⚠️ {summary['skipped']} records skipped "
                f"due to validation errors."
            )

        st.subheader("📋 Student results")

        risk_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
        display_df["sort_key"] = display_df["Status"].map(risk_order)
        display_df = display_df.sort_values("sort_key").drop(
            columns=["sort_key"]
        )
        display_df = display_df.reset_index(drop=True)
        st.dataframe(display_df)

        st.download_button(
            label="📥 Download results as CSV",
            data=display_df.to_csv(index=False),
            file_name="statussafe_batch_results.csv",
            mime="text/csv"
        )

        if skipped:
            with st.expander(
                f"⚠️ Skipped records ({len(skipped)})",
                expanded=False
            ):
                for s in skipped:
                    st.markdown(
                        f"- **{s['student_id']}** — "
                        f"{s['validation_reason']}"
                    )

        st.caption(
            "⚠️ This tool does not provide legal advice. "
            "All results are for demonstration purposes only."
        )
## Tab 3 -> ANALYTICS
with tab3:

    st.subheader("📈 Compliance analytics")
    st.markdown(
        "Historical compliance data across all batch assessments."
    )

    history      = get_batch_history()
    common_rules = get_most_common_rules()
    repeat       = get_repeat_alerts()

    if not history:
        st.info(
            "No assessment history yet. "
            "Run a batch assessment to start building analytics."
        )
    else:
        st.markdown("**📋 Assessment history**")
        history_df = pd.DataFrame(history)

        history_df["assessed_at"] = pd.to_datetime(
            history_df["assessed_at"],
            format='mixed'
        ).dt.strftime('%b %d, %Y at %H:%M')

        history_df = history_df.rename(columns={
            "batch_id":      "Batch ID",
            "assessed_by":   "Assessed by",
            "assessed_at":   "Date",
            "total_records": "Total",
            "red_count":     "🔴 RED",
            "yellow_count":  "🟡 YELLOW",
            "green_count":   "🟢 GREEN",
            "skipped_count": "Skipped"
        })
        st.dataframe(history_df)

        st.divider()

        if common_rules:
            st.markdown("**⚠️ Most triggered rules**")
            rules_df = pd.DataFrame(common_rules)
            rules_df = rules_df.rename(columns={
                "rule_id":   "Rule ID",
                "rule_name": "Rule name",
                "frequency": "Times triggered"
            })
            st.dataframe(rules_df)

        st.divider()

        st.markdown(
            "**🔁 Repeat alerts — students flagged multiple times**"
        )
        if repeat:
            repeat_df = pd.DataFrame(repeat)
            repeat_df = repeat_df.rename(columns={
                "student_id":   "Student ID",
                "alert_count":  "Times flagged",
                "last_flagged": "Last flagged"
            })
            st.dataframe(repeat_df)
        else:
            st.success(
                "✅ No repeat alerts. "
                "No student has been flagged RED more than once."
            )

        st.caption(
            "Analytics update automatically after each "
            "batch assessment."
        )
## TAB 4 -> RESOLUTION TRACKING
with tab4:

    st.subheader("✅ Resolution tracking")
    st.markdown(
        "Mark flagged students as resolved to keep your "
        "compliance records current."
    )

    repeat_for_form = get_repeat_alerts()

    if repeat_for_form:
        st.markdown("**Mark a student as resolved**")
        st.markdown(
            "Use this form to record when a compliance issue "
            "has been addressed."
        )

        with st.form("resolution_form"):
            col1, col2 = st.columns(2)

            with col1:
                student_options  = [r["student_id"] for r in repeat_for_form]
                selected_student = st.selectbox(
                    "Student ID", student_options
                )
                rule_options  = ["R001", "R002", "R003", "R004"]
                selected_rule = st.selectbox("Rule resolved", rule_options)

            with col2:
                resolved_by = st.text_input(
                    "Your name or DSO ID",
                    placeholder="e.g. DSO_Jane"
                )
                notes = st.text_area(
                    "Action taken",
                    placeholder="e.g. Student contacted, SEVIS updated",
                    height=100
                )

            resolve_submitted = st.form_submit_button(
                "Mark as resolved",
                type="primary"
            )

        if resolve_submitted:
            if not resolved_by.strip():
                st.error("Please enter your name or DSO ID.")
            elif not notes.strip():
                st.error("Please describe the action taken.")
            else:
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
                            f"✅ {selected_student} marked as resolved."
                        )
                        st.rerun()
                    else:
                        st.error("Failed to save. Try again.")
                else:
                    st.error(
                        "Could not find assessment record "
                        "for this student."
                    )
    else:
        st.success(
            "✅ No unresolved repeat alerts. "
            "All flagged students have been addressed."
        )

    st.divider()

    resolutions = get_resolutions()
    st.markdown("**📝 Resolution history**")

    if resolutions:
        res_df = pd.DataFrame(resolutions)
        res_df = res_df.rename(columns={
            "student_id":  "Student ID",
            "rule_id":     "Rule",
            "resolved_by": "Resolved by",
            "resolved_at": "Resolved at",
            "notes":       "Action taken"
        })
        st.dataframe(
            res_df[["Student ID", "Rule",
                    "Resolved by", "Resolved at", "Action taken"]]
        )
    else:
        st.info("No resolutions recorded yet.")

    st.caption(
        "⚠️ This tool does not provide legal advice. "
        "All data is for demonstration purposes only."
    )
    










































