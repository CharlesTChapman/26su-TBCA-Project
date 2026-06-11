import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

student_id = st.session_state.get('student_id')

# The student is chosen on the Home page and stored in session state.
if not student_id:
    st.warning("No student selected. Please choose a student on the home page first.")
    if st.button('Back to Home', type='primary'):
        st.switch_page('Home.py')
    st.stop()

# Back Button
if st.button("← Back", key="back_button"):
    st.switch_page(st.session_state.get('university_detail_origin', 'pages/02_Student_Data.py'))

st.title("University Details")

DEGREE_LEVELS = {1: "Bachelor's", 2: "Master's", 3: "Doctorate"}

uni_id = st.session_state.get('selected_university_id')
if not uni_id:
    st.info("No university selected. Choose one from your recommendations or favorites.")
    if st.button('Back to My Portal', type='primary'):
        st.switch_page('pages/02_Student_Data.py')
    st.stop()

# --- Fetch university data ------------------------------------------------
detail = requests.get(f"{API}/universities/{uni_id}", timeout=10)
if detail.status_code == 404:
    st.error("That university could not be found.")
    st.stop()
if detail.status_code != 200:
    st.error("Could not load this university's details.")
    st.stop()
uni = detail.json()

def show(value, fmt=None):
    """Format a value for display, falling back to a dash when missing."""
    if value is None:
        return "—"
    return fmt(value) if fmt else value

def staff_to_size(fte):
    if fte is None:
        return "—"
    if fte < 1000:
        return "Small"
    elif fte < 5000:
        return "Medium"
    else:
        return "Large"



st.divider()
st.header(uni["name"])
st.caption(show(uni.get("location")))

col1, col2, col3 = st.columns(3)
col1.metric("Est. fees per student", show(uni.get("per_student_fees"), lambda v: f"€{v:,.2f}"))
col2.metric(
    "University Size",
    staff_to_size(uni.get("staff_fte")),
    help="Based on full-time equivalent staff count: Small (<1,000), Medium (1,000–5,000), Large (5,000+)"
)
col3.metric("Highest degree", show(uni.get("highest_degree"),
                                lambda v: DEGREE_LEVELS.get(int(v), f"Level {v:g}")))

st.write(f"**University ID:** {uni.get('id')}")
st.write(f"**Location:** {show(uni.get('location'))}")
web = uni.get("web_pages")
if web:
    web = web.strip("[]'\" ")
    st.write(f"**Website:** [{web}]({web})")
else:
    st.write("**Website:** —")

st.divider()

# --- Favorite toggle ---------------------------------------------------------
favorites = requests.get(f"{API}/favorites/{student_id}", timeout=10)
favorite_ids = {fav["id"] for fav in favorites.json()} if favorites.status_code == 200 else set()
is_fav = uni_id in favorite_ids

if st.button("⭐ Favorited — click to remove" if is_fav else "☆ Add to favorites",
             type='primary', use_container_width=True):
    requests.post(f"{API}/favorites/student/{student_id}/university/{uni_id}", timeout=10)
    st.rerun()
