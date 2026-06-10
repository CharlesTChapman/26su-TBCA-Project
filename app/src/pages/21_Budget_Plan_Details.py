import logging
logger = logging.getLogger(__name__)
 
import requests
import streamlit as st
from modules.nav import SideBarLinks
 
st.set_page_config(layout="wide")
SideBarLinks()
 
API = "http://web-api:4000"
 
# The university table has no country/geo column, so map name -> country code
# here. All three demo universities are Belgian (geo='BE'). Add rows as needed.
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
        step=500_000,
        help="Split across programs based on labor-market demand.",
    )
 
recs = []
try:
    r = requests.get(
        f"{API}/budget_recommendations",
        params={"geo": geo, "total_budget": total_budget},
        timeout=15,
    )
    r.raise_for_status()
    recs = r.json().get("recommendations", [])
except Exception as e:
    logger.error(f"Could not load budget recommendations: {e}")
    st.error(f"Could not load recommendations for {university} ({geo}): {e}")
 
st.divider()
 
with st.container(border=True):
    st.subheader("Program Reallocation Table")
    st.caption(
        f"Targets are model-driven: programs feeding growing, high-absorption "
        f"sectors in {geo} gain budget; saturated or shrinking sectors get cut."
    )
    st.divider()
 
    head = st.columns([2.2, 2, 1.4, 1.6, 1.4])
    head[0].write("**Program**")
    head[1].write("**Current → Target**")
    head[2].write("**Demand**")
    head[3].write("**Budget Adj.**")
    head[4].write("**Status**")
    st.divider()
 
    status_color = {"Underfunded": ":green", "Overfunded": ":red", "Balanced": ":gray"}
 
    if not recs:
        st.info("No recommendations to show.")
    for row in recs:
        c = st.columns([2.2, 2, 1.4, 1.6, 1.4])
        c[0].write(row.get("Program", "—"))
        c[1].write(row.get("Current Target", "—"))
        c[2].write(f"{row.get('Demand Score', 0):+.2f}")
        c[3].write(row.get("Budget Adj.", "—"))
        status = row.get("Status", "—")
        prefix = status_color.get(status, "")
        c[4].write(f"{prefix}[{status}]" if prefix else status)







