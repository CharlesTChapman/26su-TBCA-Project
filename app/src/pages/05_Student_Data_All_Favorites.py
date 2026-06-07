import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

student_id = st.session_state.get('student_id')

st.title("All Favorites")

favorites = requests.get(f"{API}/favorites/{student_id}", timeout=10)
favorites = favorites.json() if favorites.status_code == 200 else []

if not favorites:
    st.write("You haven't favorited any universities yet. Add some from your recommendations.")

for fav in favorites:
    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(fav["name"])
        st.write(fav.get("location") or "")
    with col2:
        if st.button("★ Remove", key=f"fav_{fav['id']}", use_container_width=True):
            requests.post(f"{API}/favorites/{student_id}/{fav['id']}", timeout=10)
            st.rerun()
        if st.button("ℹ️ Details", key=f"det_fav_{fav['id']}", use_container_width=True):
            st.session_state['selected_university_id'] = fav["id"]
            st.session_state['university_detail_origin'] = "pages/05_Student_Data_All_Favorites.py"
            st.switch_page("pages/06_Student_Data_Unique_University_Info.py")
