import streamlit as st
import json
import os
import sys

# Ensure src is on the path
sys.path.insert(0, os.path.dirname(__file__))
from rules_engine import evaluate_rules

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