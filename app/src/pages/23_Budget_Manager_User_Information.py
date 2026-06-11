import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = 'http://web-api:4000'

manager = st.session_state.get('selected_manager', {})
manager_id = manager.get('id')

if not manager_id:
    st.warning("No budget manager selected. Please log in on the home page first.")
    if st.button('Back to Home', type='primary'):
        st.switch_page('Home.py')
    st.stop()

st.title("User Information")
st.caption("Update your account details and save.")

mgr = requests.get(f"{API}/budget_managers/{manager_id}", timeout=10)

if mgr.status_code != 200:
    st.error("Could not load your information.")
    st.stop()
mgr = mgr.json()

with st.form("edit_user_info"):
    first_name = st.text_input("First name", value=mgr.get("first_name") or "")
    last_name = st.text_input("Last name", value=mgr.get("last_name") or "")
    email = st.text_input("Email", value=mgr.get("email") or "")
    saved = st.form_submit_button("Save changes", type="primary")

if saved:
    response = requests.put(
        f"{API}/budget_managers/{manager_id}",
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
        cached = st.session_state.get('selected_manager')
        cached.update({
                "first_name": first_name, "last_name": last_name,
                "email": email,
            })
        st.session_state['first_name'] = first_name
    else:
        st.error("Could not save your changes. Please try again.")

st.divider()

if st.button("Back to Home"):
    st.switch_page("pages/20_Budget_Manager_Home.py")
