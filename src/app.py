import streamlit as st
import json
import os
import sys


# Ensure src is on the path
sys.path.insert(0, os.path.dirname(__file__))
from rules_engine import evaluate_rules, process_batch

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
    # Display resulst outside button block so it shows after assessment is run/after download button is clicked.
if "batch_output" in st.session_state:
    # process batch
    output = st.session_state["batch_output"]
    summary = output["summary"]
    results = output["results"]
    skipped = output["skipped"]
    display_df = st.session_state["batch_df"]

    st.divider()



    # Summary metrics
    st.subheader("📊 Batch Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Evaluated", summary["total_evaluated"])
    col2.metric("🔴 High Risk",    summary["red"])
    col3.metric("🟡 Moderate Risk", summary["yellow"])
    col4.metric("🟢 Compliant",    summary["green"])

    # add a complainace rate
    total = summary["total_evaluated"]
    if total > 0:
        compliance_rate = (summary["green"] / total) * 100
        st.progress(
            summary["green"] / total,
            text=f"Compliance Rate: {compliance_rate:.1f}% of students fully compliant"
        )

    if summary["skipped"] > 0:
        st.warning(
            f"⚠️ {summary['skipped']} records were skipped "
            f"due to validation errors."
         )



    # Results table
    st.subheader("📋 Student Results")
    st.dataframe(display_df)
    # Sort risk by level; RED first then YELLOW then GREEN
    risk_order = {"RED": 0, "YELLOW": 1, "GREEN": 2}
    display_df["Risk Level"] = display_df["Status"].map(risk_order)
    display_df = display_df.sort_values("Risk Level").drop(columns=["Risk Level"])  
    display_df = display_df.reset_index(drop=True)


    # Export button to download results as CSV
    st.download_button(
        label="📥 Download Results as CSV",
        data=display_df.to_csv(index=False),
        file_name="statussafe_batch_results.csv",
        mime="text/csv"
        )


    # Skipped records
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
        
        

    



