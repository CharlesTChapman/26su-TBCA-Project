import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from datetime import date, time
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

manager = st.session_state.get("selected_manager", {})

manager_name = manager.get('first_name')
st.title(f"Welcome {manager_name}")

# University Overview
st.header("Explore University Budgets")
st.divider()

# Searchable dropdown of every university
try:
    universities = load_universities()
except Exception as e:
    logger.error(f"Could not load universities from API: {e}")
    st.error(f"Could not load universities from the API: {e}")
    universities = []

university_options = {u["name"]: u for u in universities}

# Selectbox filters based on what the user types
selected_name = st.selectbox(
    "Search for a university",
    options=sorted(university_options.keys()),
    index=None,
    placeholder="Start typing to search universities...",
)

if selected_name:
    st.session_state["selected_university"] = selected_name
    if st.button(f"View budget details for {selected_name}", type="primary"):
        st.switch_page("pages/22_University_Budget_Details.py")

st.divider()

st.header("Saved Budget Plans")

manager_id = manager.get("id")

# Pairs university id with name so plans can show the university name
id_to_name = {u["id"]: u["name"] for u in universities}

plans = []
if manager_id is not None:
    try:
        r = requests.get(f"{API}/budget_plans",
                         params={"budget_manager_id": manager_id}, timeout=10)
        r.raise_for_status()
        plans = r.json()
    except Exception as e:
        logger.error(f"Could not load budget plans from API: {e}")
        st.error(f"Could not load your budget plans: {e}")

if not plans:
    st.info("You haven't saved any budget plans yet.")
    if st.button("➕ Create your first plan", type="primary"):
        st.switch_page("pages/21_Budget_Plan_Details.py")
else:
    head1, head2, head3 = st.columns([3, 2, 1])
    head1.write("**University**")
    head2.write("**Total Budget**")
    head3.write("**Actions**")
    st.divider()

    for plan in plans:
        uni_name = id_to_name.get(plan["university_id"], f"University #{plan['university_id']}")
        total = plan.get("total_amount")
        c1, c2, c3 = st.columns([3, 2, 1])
        c1.write(uni_name)
        c2.write(f"€{total:,}" if total is not None else "—")
        with c3:
            if st.button("View Plan", key=f"plan_{plan['id']}", use_container_width=True):
                st.session_state["selected_university"] = uni_name
                st.session_state["selected_plan_id"] = plan["id"]
                st.switch_page("pages/21_Budget_Plan_Details.py")

    st.divider()
    if st.button("➕ Create new plan", type="primary"):
        st.switch_page("pages/21_Budget_Plan_Details.py")
