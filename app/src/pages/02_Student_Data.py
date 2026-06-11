import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks
from modules.favorites_ui import render_favorites, format_fees
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

student_id = st.session_state.get('student_id') # Pulls current student id in session

# The student is chosen on the Home page and stored in session state.
if not student_id:
    st.warning("No student selected. Please choose a student on the home page first.")
    if st.button('Back to Home', type='primary'):
        st.switch_page('Home.py')
    st.stop()

student_survey = requests.get(f"{API}/survey_form/{student_id}", timeout=120)

if student_survey.status_code != 200:
    st.error("Could not load your survey data. Please retake the survey.")
    st.stop()

student_survey = student_survey.json()

rec_response = requests.get(
    f"{API}/modelrec/predict/{student_survey['student_budget']}/{student_survey['student_degree_level']}/{student_survey['student_size']}",
    params={
        "country": student_survey.get("student_country"),
        "max_km": student_survey.get("student_proximity_max")
    },
    timeout=300
)

if rec_response.status_code == 200:
    raw = rec_response.json()
    results = [
        {"rank": rank, "name": data["name"], "city": data["city"], "match score": data["match_number"]}
        for rank, data in raw.items()
    ]
else:
    st.error(f"Could not load recommendations. Response code: {rec_response.status_code}")
    st.stop()

st.title("My Portal")

st.write(
   "Here lies all your information regarding universities decisions. Good Luck!"
)


# Favorites 
# Recommendations only carry a name, so map name -> id in order to favorite them.
universities = requests.get(f"{API}/universities", timeout=10)
uni_by_name = {u["name"]: u for u in universities.json()} if universities.status_code == 200 else {}

favorites = requests.get(f"{API}/favorites/{student_id}", timeout=10)
favorites = favorites.json() if favorites.status_code == 200 else []
favorite_ids = {fav["id"] for fav in favorites}


def toggle_favorite(university_id):
    """Add/remove a favorite, then refresh the page to reflect the change."""
    requests.post(f"{API}/favorites/student/{student_id}/university/{university_id}", timeout=10)
    st.rerun()


def view_details(university_id):
    """Open the full-details page for a given university."""
    st.session_state['selected_university_id'] = university_id
    st.session_state['university_detail_origin'] = "pages/02_Student_Data.py"
    st.switch_page("pages/06_Student_Data_Unique_University_Info.py")


left, right = st.columns(2)

with left:
    with st.container(border = True):
        st.subheader("Personalized University Recommendations")
        st.divider()
        for rec_index, university in enumerate(results):
            # Separate each university
            if rec_index > 0:
                st.divider()
            uni_record = uni_by_name.get(university["name"], {})
            uni_id = uni_record.get("id")
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{university['rank']} - {university['name']}")
                st.write(
                    f"{university['city']} | {university['match score']} match score"
                    f" | {format_fees(uni_record.get('per_student_fees'))}"
                )
            with col2:
                is_fav = uni_id in favorite_ids
                if st.button("⭐ Favorited" if is_fav else "☆ Favorite",
                             key=f"rec_{university['name']}", use_container_width=True):
                    if uni_id is not None:
                        toggle_favorite(uni_id)
                if uni_id is not None and st.button(
                        "ℹ️ Details", key=f"det_rec_{university['name']}",
                        use_container_width=True):
                    view_details(uni_id)
        st.divider()
        if st.button("View More", key="view_more_results", use_container_width=True):
            st.switch_page("pages/03_Student_Data_Universities_List.py")

with right:

    with st.container(border = True):
        st.subheader("Favorites")
        st.divider()
        render_favorites(
            API, student_id, favorites,
            origin_page="pages/02_Student_Data.py",
            key_prefix="overview_fav",
            limit=5,
        )
        st.divider()
        if st.button("View More", key="view_more_favorites", use_container_width=True):
            st.switch_page("pages/05_Student_Data_All_Favorites.py")


    