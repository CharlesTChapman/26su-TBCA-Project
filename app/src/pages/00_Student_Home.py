import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API = 'http://web-api:4000'

st.title("Student Portal")
st.write("Select your name to view your portal or take the survey.")

# Load students from REST API

response = requests.get(f"{API}/students")

if response.status_code != 200:
    st.error("Could not load student data.")
    st.stop()


students = response.json()
    

# Map student full names (ex: Maria Lopez) to their student record, rather than by index

selected = st.selectbox("Select your name", students, 
                        format_func = lambda s: f"{s['first_name']} {s['last_name']}")

if selected:

    st.header(f"Welcome {selected['first_name']}")

    st.session_state['student_id'] = selected['id']

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Name:** {selected['first_name']} {selected['last_name']}")
        st.write(f"**Email:** {selected['email']}")
    with col2:
        st.write(f"**Major:** {selected['major']}")
        st.write(f"**Address:** {selected['address']}")

    st.divider()


    # Check if this student has completed the survey
    survey_check = requests.get(f"{API}/survey_form/{selected['id']}")

    if survey_check.status_code == 200:
        st.success("You have already completed the survey.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button('Go to My Portal', type='primary', use_container_width=True):
                st.switch_page('pages/02_Student_Data.py')
        with col2:
            if st.button('Retake Survey', use_container_width=True):
                st.switch_page('pages/01_Student_Survey.py')
    else:
        st.write("Click the following to start your journey!")
        if st.button('Take the Student Survey', type='primary', use_container_width=True):
            st.switch_page('pages/01_Student_Survey.py')