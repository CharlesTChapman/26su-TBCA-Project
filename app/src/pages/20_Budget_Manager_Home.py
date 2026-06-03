import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Budget Manager Dashboard")

# University Overview
st.header("University Review")
st.divider()

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border = True):
        st.write("**Flagged Universities**")
        st.title("7")

with col2:
    with st.container(border=True):
        st.write("**Plans Drafted**")
        st.title("2")

with col3:
    with st.container(border=True):
        st.write("**Submission Deadline**")
        st.title("07/15/2025")

st.divider()

# University Listing (Alphabetical Order)
data = [
    {"Program" : "Ghent University", "Total Budget": "€45.23M (12%)", "Misaligned": "1 Program", "Plan": "Drafted"},
    {"Program" : "KU Leuven", "Total Budget": "€30.12M (8%)", "Misaligned": "2 Programs", "Plan": "Not Drafted"},
    {"Program" : "Université Libre de Bruxelles (ULB)", "Total Budget": "€20.78M (5%)", "Misaligned": "3 Programs", "Plan": "Not Drafted"}
]

st.header("University List")
st.write("")
st.write("")
st.write("")

col1, col2, col3, col4, col5 = st.columns(5)
col1.write("**Program**")
col2.write("**Total Budget**")
col3.write("**Misaligned**")
col4.write("**Plan**")
col5.write("**Actions**")


st.divider()

for row in data:
    with st.container():
        col1, col2, col3, col4, col5 = st.columns(5)
        col1.write(row["Program"])
        col2.write(row["Total Budget"])
        col3.write(row["Misaligned"])
        col4.write(row["Plan"])

        with col5:
            if st.button("View Plan", key=row["Program"], use_container_width = True):
                st.session_state["selected_university"] = row["Program"]
                st.switch_page("pages/21_Budget_Plan_Details.py")
