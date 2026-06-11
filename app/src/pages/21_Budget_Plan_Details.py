import logging
logger = logging.getLogger(__name__)

import requests
import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout="wide")
SideBarLinks()

API = "http://web-api:4000"

COUNTRY_BY_UNIVERSITY = {
    "KU Leuven": "BE",
    "Ghent University": "BE",
    "Université Libre de Bruxelles (ULB)": "BE",
}

university = st.session_state.get("selected_university", "Unknown University")
geo = COUNTRY_BY_UNIVERSITY.get(university, "BE")

st.title("Budget Plan Details")
st.header(f"{university} Budget Plan Details")
st.divider()

col_a, _ = st.columns([1, 3])
with col_a:
    total_budget = st.number_input(
        "Total program budget (€)",
        min_value=0,
        value=12_000_000,
        step=50_000,
        help="Split across every major based on labor-market demand and enrollment.",
    )

recs = []
n_students = 0
try:
    r = requests.get(
        f"{API}/budget_recommendations/students",
        params={"geo": geo, "total_budget": total_budget},
        timeout=15,
    )
    r.raise_for_status()
    payload = r.json()
    recs = payload.get("recommendations", [])
    n_students = payload.get("n_students", 0)
except Exception as e:
    logger.error(f"Could not load budget recommendations: {e}")
    st.error(f"Could not load recommendations for {university} ({geo}): {e}")

st.divider()

with st.container(border=True):
    st.subheader("Program Reallocation Table")
    st.caption(
        f"Targets are model-driven across all {len(recs)} majors, starting from "
        f"current enrollment ({n_students} students). Majors feeding growing, "
        f"high-absorption sectors in {geo} gain budget; saturated or shrinking "
        f"sectors get cut."
    )
    st.divider()

    widths = [2.4, 2.2, 1.7, 1.2, 1.6, 1.5, 1.2]
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
        c[0].write(row.get("Program", "—"))
        c[1].write(row.get("Current Target", "—"))
        c[2].write(f"{row.get('Demand Score', 0):+.2f}")
        c[3].write(row.get("Budget Adj.", "—"))
        target_amt = row.get("Target Amount")
        c[4].write(f"€{target_amt:,.0f}" if target_amt is not None else "—")
        status = row.get("Status", "—")
        prefix = status_color.get(status, "")
        c[5].write(f"{prefix}[{status}]" if prefix else status)

    if recs:
        st.divider()
        total_alloc = sum(r.get("Target Amount", 0) or 0 for r in recs)
        st.caption(f"Allocated: €{total_alloc:,.0f} of €{total_budget:,.0f}")






