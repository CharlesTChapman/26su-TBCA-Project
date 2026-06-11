import logging

import requests
import streamlit as st

from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout="wide")
SideBarLinks()

API = "http://web-api:4000"


# Format Helper Functions
def _g(row, *keys, default=None):
    """Return the first present key from a row (handles differing field names)."""
    for k in keys:
        if row.get(k) is not None:
            return row[k]
    return default


def _fmt_demand(v):
    if isinstance(v, (int, float)):
        return f"{v:+.2f}"
    return v if v is not None else "—"


def _fmt_money(v):
    if isinstance(v, (int, float)):
        return f"€{v:,.0f}"
    return v if v is not None else "—"


def _amount_raw(row):
    raw = row.get("_target_amount_raw")
    if isinstance(raw, (int, float)):
        return raw
    v = row.get("Target Amount")
    if isinstance(v, (int, float)):
        return v
    if isinstance(v, str):
        try:
            return float(v.replace("€", "").replace(",", "").strip())
        except ValueError:
            return 0.0
    return 0.0


@st.cache_data(ttl=300)
def load_universities():
    """Fetch all universities from the API's GET /universities route."""
    r = requests.get(f"{API}/universities", timeout=10)
    r.raise_for_status()
    return r.json()


if st.button("← Back", key="back_button"):
    st.switch_page("pages/20_Budget_Manager_Home.py")

st.title("Budget Plan Details")

# Pick University
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

# Country comes from the selected university's record (university.country).
geo = uni.get("country")
st.session_state["selected_country"] = geo

# Get Data
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

student_fees = uni.get("student_fees")
plan_amount = uni.get("student_fees") if student_fees else 0

# Current Standing
st.divider()
st.header(selected_name)
st.caption(uni.get("location") or "")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Budget",
            f"€{student_fees:,.0f}" if student_fees is not None else "—",
            help="The university's reported total student-fee revenue.")
col2.metric("Total Students",
            f"{num_students:,}" if num_students is not None else "—")
col3.metric("Graduation Rate",
            f"{graduation_rate:.1%}" if graduation_rate is not None else "—")
col4.metric("Country", geo or "Unknown")

if report_year is not None:
    st.caption(f"📅 Academic figures are from the {report_year} report.")

# Save a plan
st.divider()
st.subheader("Save Budget Plan")

manager = st.session_state.get("selected_manager", {})
manager_id = manager.get("id")

# Load existing plan for the selected university
existing_plan = None
if manager_id is not None:
    try:
        lookup = requests.get(
            f"{API}/budget_plans",
            params={"budget_manager_id": manager_id},
            timeout=10,
        )
        if lookup.status_code == 200:
            existing_plan = next(
                (p for p in lookup.json() if p.get("university_id") == uni_id),
                None,
            )
    except Exception as e:
        logger.error(f"Could not load existing budget plans: {e}")

# Default to the saved plan's amount when one exists, else student fees
default_amount = (
    int(existing_plan["total_amount"])
    if existing_plan and existing_plan.get("total_amount") is not None
    else (int(student_fees) if student_fees else 0)
)

# Refresh the input when the university changes
arrived_via_view = st.session_state.pop("selected_plan_id", None) is not None
if st.session_state.get("_plan_amount_uni") != uni_id or arrived_via_view:
    st.session_state["_plan_amount_uni"] = uni_id
    st.session_state["save_plan_amount"] = default_amount

if manager_id is None:
    st.warning("Log in as a budget manager from the home page to save a plan.")
else:
    plan_amount = st.number_input(
        "Budget amount for this plan (€)",
        min_value=0,
        step=100_000,
        key="save_plan_amount",
    )
    if st.button("Save budget plan", type="primary"):
        try:
            payload = {
                "university_id": uni_id,
                "budget_manager_id": manager_id,
                "total_amount": int(plan_amount),
            }
            # Update the existing plan if there is one, otherwise create it.
            if existing_plan is not None:
                resp = requests.put(
                    f"{API}/budget_plans/{existing_plan['id']}", json=payload, timeout=10)
            else:
                resp = requests.post(
                    f"{API}/budget_plans", json=payload, timeout=10)

            if resp.status_code in (200, 201):
                st.success(
                    f"Saved budget plan for {selected_name} (€{int(plan_amount):,}).")
            else:
                st.error("Could not save the budget plan. Please try again.")
        except Exception as e:
            logger.error(f"Failed to save budget plan: {e}")
            st.error(f"Could not save the budget plan: {e}")

# Sector reallocation (labor-market ML model) 
# This step needs the university's country to pull the right labor-market data.
if not geo:
    st.warning(
        f"No country is on file for {selected_name}, so labor-market budget "
        "recommendations can't be generated."
    )
    st.stop()

st.divider()
st.header(f"{selected_name} — Suggested Sector Reallocations")

recs = []
n_students = 0
try:
    r = requests.get(
        f"{API}/budget_recommendations/students",
        params={"geo": geo, "total_budget": plan_amount},
        timeout=15,
    )
    r.raise_for_status()
    payload = r.json()
    recs = payload.get("recommendations", [])
    n_students = payload.get("n_students", 0)
except Exception as e:
    logger.error(f"Could not load budget recommendations for {geo}: {e}")
    st.error(f"Could not load recommendations for {selected_name} ({geo}): {e}")

with st.container(border=True):
    st.subheader("Program Reallocation Table")
    st.caption(
        f"Targets are model-driven across all {len(recs)} majors, starting from "
        f"current enrollment ({n_students} students). Majors feeding growing, "
        f"high-absorption sectors in {geo} gain budget; saturated or shrinking "
        f"sectors get cut."
    )
    st.divider()

    widths = [2.4, 2.2, 1.7, 1.4, 1.6, 1.3]
    head = st.columns(widths)
    head[0].write("**Major**")
    head[1].write("**Current → Target**")
    head[2].write("**Demand**")
    head[3].write("**Budget Adj.**")
    head[4].write("**Target Amount**")
    head[5].write("**Status**")
    st.divider()

    status_color = {"Underfunded": ":green", "Overfunded": ":red", "Balanced": ":gray"}

    if not recs:
        st.info("No recommendations to show.")

    for row in recs:
        c = st.columns(widths)
        c[0].write(_g(row, "Major", "Program", default="—"))
        c[1].write(_g(row, "Current → Target", "Current Target", default="—"))
        c[2].write(_fmt_demand(_g(row, "Demand", "Demand Score")))
        c[3].write(_g(row, "Budget Adj.", default="—"))
        c[4].write(_fmt_money(_g(row, "Target Amount")))
        status = _g(row, "Status", default="—")
        prefix = status_color.get(status, "")
        c[5].write(f"{prefix}[{status}]" if prefix else status)

    if recs:
        st.divider()
        total_alloc = sum(_amount_raw(r) for r in recs)
        st.caption(f"Allocated: €{total_alloc:,.0f} of €{plan_amount:,.0f}")