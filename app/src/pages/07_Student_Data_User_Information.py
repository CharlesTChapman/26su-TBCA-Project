import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = 'http://web-api:4000'

student_id = st.session_state.get('student_id')

if not student_id:
    st.warning("No student selected. Please choose a student on the home page first.")
    if st.button('Back to Home', type='primary'):
        st.switch_page('Home.py')
    st.stop()

st.title("User Information")
st.caption("Update your account details and save.")

student = requests.get(f"{API}/students/{student_id}", timeout=10)

if student.status_code != 200:
    st.error("Could not load your information.")
    st.stop()
student = student.json()

with st.form("edit_user_info"):
    first_name = st.text_input("First name", value=student.get("first_name") or "")
    last_name = st.text_input("Last name", value=student.get("last_name") or "")
    email = st.text_input("Email", value=student.get("email") or "")
    address = st.text_input("Address", value=student.get("address") or "")
    major = st.text_input("Major", value=student.get("major") or "")
    saved = st.form_submit_button("Save changes", type="primary")

if saved:
    response = requests.put(
        f"{API}/students/{student_id}",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "address": address,
            "major": major,
        },
        timeout=10,
    )
    if response.status_code == 200:
        st.success("Your information has been updated.")
        st.cache_data.clear()
        cached = st.session_state.get('selected_student')
        cached.update({
                "first_name": first_name, "last_name": last_name,
                "email": email, "address": address, "major": major,
            })
        st.session_state['first_name'] = first_name
    else:
        st.error("Could not save your changes. Please try again.")

st.divider()

if st.button("Back to Home"):
    st.switch_page("pages/00_Student_Home.py")
