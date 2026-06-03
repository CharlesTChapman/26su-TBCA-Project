import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("My Portal")

st.write(
   "Here lies all yor information regarding universities decisions. Good Luck!"
)

results = [
    {"University": "University A", "Acceptance Rate": "20%", "Average SAT": 1400, "Average GPA": 3.8},
    {"University": "University B", "Acceptance Rate": "35%", "Average SAT": 1300, "Average GPA": 3.5},
    {"University": "University C", "Acceptance Rate": "50%", "Average SAT": 1200, "Average GPA": 3.2},
]





