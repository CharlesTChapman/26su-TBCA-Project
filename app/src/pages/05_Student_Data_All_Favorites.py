import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("All Favorites")

results = [
    {"rank": 1, "name": "University of Antwerp", "country": "Belgium", "size": "Medium", "type": "Public", "tuition": 1100},
    {"rank": 2, "name": "KU Leuven", "country": "Belgium", "size": "Large", "type": "Public", "tuition": 1200},
    {"rank": 3, "name": "Université Libre de Bruxelles (ULB)", "country": "Belgium", "size": "Medium", "type": "Public", "tuition": 1250},
    {"rank": 4, "name": "Ghent University", "country": "Belgium", "size": "Large", "type": "Public", "tuition": 1000},
    {"rank": 5, "name": "Université catholique de Louvain (UCLouvain)", "country": "Belgium", "size": "Medium", "type": "Private", "tuition": 1300},
    {"rank": 6, "name": "University of Ghent", "country": "Belgium", "size": "Large", "type": "Public", "tuition": 1050},
    {"rank": 7, "name": "Université de Liège", "country": "Belgium", "size": "Medium", "type": "Public", "tuition": 1150},
    {"rank": 8, "name": "Université de Namur", "country": "Belgium", "size": "Small", "type": "Private", "tuition": 1250},
    {"rank": 9, "name": "Université de Mons", "country": "Belgium", "size": "Small", "type": "Public", "tuition": 1100},
    {"rank": 10, "name": "Université de Louvain-la-Neuve (UCLouvain)", "country": "Belgium", "size": "Medium", "type": "Private", "tuition": 1300},

]

for university in results: 
    col1, col2 = st.columns([3,1])
    with col1:
        st.subheader(f"{university['rank']} - {university['name']}")
        st.write(f"{university['country']} | {university['size']} | {university['type']} | {university['tuition']:,}/yr")
    with col2:
        if st.button("Learn More", key = university["name"], use_container_width = True):
            st.session_state["selected_university"] = university["name"]
            st.switch_page("pages/04_Student_Data_University_Details.py")