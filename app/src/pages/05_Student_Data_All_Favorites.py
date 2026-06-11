import logging
logger = logging.getLogger(__name__)

import streamlit as st
from modules.nav import SideBarLinks
from modules.favorites_ui import render_favorites
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

student_id = st.session_state.get('student_id')

st.title("All Favorites")

favorites = requests.get(f"{API}/favorites/{student_id}", timeout=10)
favorites = favorites.json() if favorites.status_code == 200 else []

render_favorites(
    API, student_id, favorites,
    origin_page="pages/05_Student_Data_All_Favorites.py",
    key_prefix="all_fav",
)
