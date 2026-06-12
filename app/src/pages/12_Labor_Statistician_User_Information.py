import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = 'http://web-api:4000'

statistician = st.session_state.get('selected_statistician', {})
statistician_id = statistician.get('id')

if not statistician_id:
    st.warning("No labor statistician selected. Please log in on the home page first.")
    if st.button('Back to Home', type='primary'):
        st.switch_page('Home.py')
    st.stop()

st.title("User Information")
st.caption("Update your account details and save.")

stat = requests.get(f"{API}/labor_statisticians/{statistician_id}", timeout=10)

if stat.status_code != 200:
    st.error("Could not load your information.")
    st.stop()
stat = stat.json()

with st.form("edit_user_info"):
    first_name = st.text_input("First name", value=stat.get("first_name") or "")
    last_name = st.text_input("Last name", value=stat.get("last_name") or "")
    email = st.text_input("Email", value=stat.get("email") or "")
    saved = st.form_submit_button("Save changes", type="primary")

if saved:
    response = requests.put(
        f"{API}/labor_statisticians/{statistician_id}",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
        },
        timeout=10,
    )
    if response.status_code == 200:
        st.success("Your information has been updated.")
        st.cache_data.clear()
        cached = st.session_state.get('selected_statistician')
        cached.update({
                "first_name": first_name, "last_name": last_name,
                "email": email,
            })
        st.session_state['first_name'] = first_name
    else:
        st.error("Could not save your changes. Please try again.")

st.divider()

if st.button("Back to Home"):
    st.switch_page("pages/10_Labor_Statistician_Home.py")
