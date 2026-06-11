import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
from modules.favorites_ui import format_fees
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

student_id = st.session_state.get('student_id')

# --- Survey + full recommendation ranking -------------------------------------
student_survey = requests.get(f"{API}/survey_form/{student_id}", timeout=10)
if student_survey.status_code != 200:
    st.error("Could not load your survey data. Please retake the survey.")
    st.stop()
student_survey = student_survey.json()

rec_response = requests.get(
    f"{API}/modelrec/predict/all/{student_survey['student_budget']}/{student_survey['student_degree_level']}/{student_survey['student_size']}",
    timeout=60
)
if rec_response.status_code != 200:
    st.error("Could not load recommendations.")
    st.stop()

results = [
    {"rank": rank, "name": data["name"], "city": data["city"], "match score": data["match_number"]}
    for rank, data in rec_response.json().items()
][:100]

# --- Favorites lookup ---------------------------------------------------------
# Recommendations only carry a name, so map name -> id in order to favorite them.
universities = requests.get(f"{API}/universities", timeout=10)
uni_by_name = {u["name"]: u for u in universities.json()} if universities.status_code == 200 else {}

favorites = requests.get(f"{API}/favorites/{student_id}", timeout=10)
favorite_ids = {fav["id"] for fav in favorites.json()} if favorites.status_code == 200 else set()

st.title("Personalized University Recommendations")
st.caption("Top 50 matches based on your survey. Star any to add it to your favorites.")

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
                requests.post(f"{API}/favorites/student/{student_id}/university/{uni_id}", timeout=10)
                st.rerun()
        if uni_id is not None and st.button(
                "ℹ️ Details", key=f"det_rec_{university['name']}",
                use_container_width=True):
            st.session_state['selected_university_id'] = uni_id
            st.session_state['university_detail_origin'] = "pages/03_Student_Data_Universities_List.py"
            st.switch_page("pages/06_Student_Data_Unique_University_Info.py")
