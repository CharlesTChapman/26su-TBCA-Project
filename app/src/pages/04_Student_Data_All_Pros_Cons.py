import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

student_id = st.session_state.get('student_id')
uni_id = st.session_state.get('selected_university_id')

if not student_id:
    st.warning("No student selected. Please choose a student on the home page first.")
    if st.button('Back to Home', type='primary'):
        st.switch_page('Home.py')
    st.stop()

if not uni_id:
    st.info("No university selected. Open a university's details to view and edit its pros and cons.")
    if st.button('Go to My Recommendations', type='primary'):
        st.switch_page('pages/03_Student_Data_Universities_List.py')
    st.stop()

# Back Button
if st.button("← Back", key="back_button"):
    st.switch_page(st.session_state.get(
        'pros_cons_origin', 'pages/06_Student_Data_Unique_University_Info.py'))

# University name for the header 
uni = requests.get(f"{API}/universities/{uni_id}", timeout=10)
uni_name = uni.json().get("name") if uni.status_code == 200 else f"University {uni_id}"

st.title("Pros and Cons")
st.header(uni_name)

# Load existing pros/cons

pros_cons = requests.get(
    f"{API}/pros_cons/student/{student_id}/university/{uni_id}", timeout=10)
record_exists = pros_cons.status_code == 200
record = pros_cons.json() if record_exists else {}

st.caption("Enter one pro or con per line, then save.")

with st.form("pros_cons_form"):
    pros_col, cons_col = st.columns(2)
    with pros_col:
        st.subheader("Pros")
        new_pros = st.text_area(
            "Pros", value=record.get("pros") or "", height=300, label_visibility="collapsed")
    with cons_col:
        st.subheader("Cons")
        new_cons = st.text_area(
            "Cons", value=record.get("cons") or "", height=300, label_visibility="collapsed")
    submitted = st.form_submit_button("Save", type="primary", use_container_width=True)

if submitted:
    def clean(text):
        """Drop blank lines and surrounding whitespace."""
        return "\n".join(line.strip() for line in text.splitlines() if line.strip())

    payload = {"pros": clean(new_pros), "cons": clean(new_cons)}
    if record_exists:
        resp = requests.put(
            f"{API}/pros_cons/student/{student_id}/university/{uni_id}", json=payload, timeout=10)
    else:
        resp = requests.post(
            f"{API}/pros_cons/student/{student_id}/university/{uni_id}", json=payload, timeout=10)

    if resp.status_code in (200, 201):
        st.success("Saved!")
        st.rerun()
    elif resp.status_code == 404:
        st.info("No changes to save.")
    else:
        st.error("Could not save your pros and cons.")
