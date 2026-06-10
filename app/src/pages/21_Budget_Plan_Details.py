import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"


@st.cache_data(ttl=300)
def load_universities():
    """Fetch all universities from the API's GET /universities route."""
    r = requests.get(f"{API}/universities", timeout=10)
    r.raise_for_status()
    return r.json()


if st.button("← Back", key="back_button"):
    st.switch_page("pages/20_Budget_Manager_Home.py")

st.title("Budget Plan Details")

# --- Pick a university --------------------------------------------------------
try:
    universities = load_universities()
except Exception as e:
    logger.error(f"Could not load universities from API: {e}")
    st.error(f"Could not load universities from the API: {e}")
    st.stop()

options = {u["name"]: u for u in universities}
names = sorted(options.keys())

preset = st.session_state.get("selected_university")
default_index = names.index(preset) if preset in options else None

selected_name = st.selectbox(
    "University",
    options=names,
    index=default_index,
    placeholder="Search for a university...",
)

if not selected_name:
    st.info("Select a university to build its budget plan.")
    st.stop()

uni = options[selected_name]
uni_id = uni["id"]
st.session_state["selected_university"] = selected_name

# --- Gather the figures -------------------------------------------------------
num_students = None
graduation_rate = None
report_year = None
try:
    r = requests.get(f"{API}/stats/universities/{uni_id}", timeout=10)
    if r.status_code == 200:
        reports = [row for row in r.json() if row.get("year") is not None]
        if reports:
            latest = max(reports, key=lambda row: row["year"])
            num_students = latest.get("students")
            graduation_rate = latest.get("graduation_rate")
            report_year = latest.get("year")
except Exception as e:
    logger.error(f"Could not load academic stats for university {uni_id}: {e}")

total_budget = uni.get("student_fees")

fee_per_student = None
if total_budget is not None and num_students:
    fee_per_student = total_budget / num_students

# --- Current standing ---------------------------------------------------------
st.divider()
st.header(selected_name)
st.caption(uni.get("location") or "")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Budget",
            f"€{total_budget:,.0f}" if total_budget is not None else "—",
            help="The university's reported total student-fee revenue.")
col2.metric("Total Students",
            f"{num_students:,}" if num_students is not None else "—")
col3.metric("Graduation Rate",
            f"{graduation_rate:.1%}" if graduation_rate is not None else "—")
col4.metric("Budget Efficiency Score", "—")

if report_year is not None:
    st.caption(f"📅 Academic figures are from the {report_year} report.")

# --- Save a budget plan -------------------------------------------------------
st.divider()
st.subheader("💾 Save Budget Plan")

manager = st.session_state.get("selected_manager", {})
manager_id = manager.get("id")

if manager_id is None:
    st.warning("Log in as a budget manager from the home page to save a plan.")
else:
    plan_amount = st.number_input(
        "Budget amount for this plan (€)",
        min_value=0,
        value=int(total_budget) if total_budget else 0,
        step=100_000,
        key="save_plan_amount",
    )
    if st.button("Save budget plan", type="primary"):
        try:
            resp = requests.post(
                f"{API}/budget_plans",
                json={
                    "university_id": uni_id,
                    "budget_manager_id": manager_id,
                    "total_amount": int(plan_amount),
                },
                timeout=10,
            )
            if resp.status_code == 201:
                st.success(
                    f"Saved budget plan for {selected_name} (€{int(plan_amount):,}).")
            else:
                st.error("Could not save the budget plan. Please try again.")
        except Exception as e:
            logger.error(f"Failed to save budget plan: {e}")
            st.error(f"Could not save the budget plan: {e}")

# --- Approximate student performance from a proposed budget -------------------
st.divider()
st.subheader("📈 Approximate Student Performance")
st.write("Enter a proposed total budget to estimate the resulting student performance.")

proposed_budget = st.number_input(
    "Proposed total budget (€)",
    min_value=0,
    value=int(total_budget) if total_budget else 0,
    step=100_000,
)

if st.button("Approximate performance"):
    performance = None # replace with ml model prediction
    if performance is None:
        st.info("🔮 The student-performance model hasn't been built yet — "
                "the estimate will appear here once it's implemented.")
    else:
        st.metric("Approx. Student Performance", performance)

# --- Predict the ideal budget -------------------------------------------------
st.divider()
st.subheader("🎯 Predict Ideal Budget")
st.write("Estimate the budget that would optimize student performance for this university.")

if st.button("Predict ideal budget"):
    ideal_budget = None # replace with ml model prediction
    if ideal_budget is None:
        st.info("🔮 The ideal-budget model hasn't been built yet — "
                "the prediction will appear here once it's implemented.")
    else:
        st.metric("Predicted Ideal Budget", f"€{ideal_budget:,.0f}")
