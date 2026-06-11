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


# Back to the budget manager dashboard.
if st.button("← Back", key="back_button"):
    st.switch_page("pages/20_Budget_Manager_Home.py")

st.title("University Budget Details")

# Pick a university
try:
    universities = load_universities()
except Exception as e:
    logger.error(f"Could not load universities from API: {e}")
    st.error(f"Could not load universities from the API: {e}")
    st.stop()

options = {u["name"]: u for u in universities}
names = sorted(options.keys())

# Pre-select whatever university was chosen on the dashboard, if any.
preset = st.session_state.get("selected_university")
default_index = names.index(preset) if preset in options else None

selected_name = st.selectbox(
    "University",
    options=names,
    index=default_index,
    placeholder="Search for a university...",
)

if not selected_name:
    st.info("Select a university to view its budget details.")
    st.stop()

uni = options[selected_name]
uni_id = uni["id"]
st.session_state["selected_university"] = selected_name

# Gather the figures 
    # Total students and graduation rate from the most recent academic report.
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

# University budget: the university's reported total student-fee revenue.
# (student_fees is already an aggregate figure, so it is not multiplied.)
total_budget = uni.get("student_fees")

# Average fee per student, derived from the budget and the latest enrollment.
fee_per_student = None
if total_budget is not None and num_students:
    fee_per_student = total_budget / num_students

# How many students have favorited this university.
favorite_count = None
try:
    r = requests.get(f"{API}/stats/universities/{uni_id}/favorites", timeout=10)
    if r.status_code == 200:
        favorite_count = r.json().get("favorite_count")
except Exception as e:
    logger.error(f"Could not load favorite count for university {uni_id}: {e}")

# Display 
st.divider()
st.header(selected_name)
st.caption(uni.get("location") or "")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Budget",
            f"€{total_budget:,.0f}" if total_budget is not None else "—",
            help="The university's reported total student-fee revenue.")
col2.metric("Total Students",
            f"{num_students:,}" if num_students is not None else "—")
col3.metric("Graduation Rate",
            f"{graduation_rate:.1%}" if graduation_rate is not None else "—")
col4.metric("Budget Efficiency Score", "—")
col5.metric("Student Favorites",
            f"{favorite_count:,}" if favorite_count is not None else "—")

if report_year is not None:
    st.caption(f"📅 Academic figures are from the {report_year} report.")

st.divider()

if st.button(f"Create budget plan for {selected_name}", type="primary"):
    st.switch_page("pages/21_Budget_Plan_Details.py")

