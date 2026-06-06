import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

student_id = st.session_state.get('student_id') # Pulls current student id in session
student_survey = requests.get(f"{API}/survey_form/{student_id}", timeout=10)

if student_survey.status_code != 200:
    st.error("Could not load your survey data. Please retake the survey.")
    st.stop()

student_survey = student_survey.json()

rec_response = requests.get(
    f"{API}/modelrec/predict/{student_survey['student_budget']}/{student_survey['student_degree_level']}/{student_survey['student_size']}",
    timeout=50
)

if rec_response.status_code == 200:
    raw = rec_response.json()
    results = [
        {"rank": rank, "name": data["name"], "city": data["city"], "match": data["match_number"]}
        for rank, data in raw.items()
    ]
else:
    st.error("Could not load recommendations.")
    st.stop()

st.title("My Portal")

st.write(
   "Here lies all yor information regarding universities decisions. Good Luck!"
)


#Temp Data
favorites = [
    {"rank": 1, "name": "University of Antwerp", "country": "Belgium", "size": "Medium", "type": "Public", "tuition": 1100},
    {"rank": 2, "name": "KU Leuven", "country": "Belgium", "size": "Large", "type": "Public", "tuition": 1200},
    {"rank": 3, "name": "Université Libre de Bruxelles (ULB)", "country": "Belgium", "size": "Medium", "type": "Public", "tuition": 1250},
    {"rank": 4, "name": "Ghent University", "country": "Belgium", "size": "Large", "type": "Public", "tuition": 1000},
    {"rank": 5, "name": "Université catholique de Louvain (UCLouvain)", "country": "Belgium", "size": "Medium", "type": "Private", "tuition": 1300},

]


left, right = st.columns(2)

with left:
    with st.container(border = True):
        st.subheader("Personalized University Recommendations")
        st.divider()
        for university in results:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{university['rank']} - {university['name']}")
                st.write(f"{university['city']} | {university['match']}% match")
            with col2:
                if st.button("Learn More", key=university["name"], use_container_width=True):
                    st.session_state["selected_university"] = university["name"]

        st.divider()
        if st.button("View More", key="view_more_results", use_container_width=True):
            st.switch_page("pages/03_Student_Data_Universities_List.py")

with right:

    with st.container(border = True):
        st.subheader("Favorites")
        st.divider()
        for university in favorites: 
            col1, col2 = st.columns([3,1])
            with col1:
                st.subheader(f"{university['rank']} - {university['name']}")
                st.write(f"{university['country']} | {university['size']} | {university['type']} | {university['tuition']:,}/yr")
            with col2:
                if st.button("Learn More", key = university["name"] + "_fav", use_container_width = True):
                    st.session_state["selected_university"] = university["name"]
        st.divider()
        if st.button("View More", key="view_more_favorites", use_container_width=True):
            st.switch_page("pages/05_Student_Data_All_Favorites.py")


    