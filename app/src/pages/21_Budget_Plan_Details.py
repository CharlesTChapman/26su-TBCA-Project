import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()


st.title("Budget Plan Details")

university = st.session_state.get("selected_university", "Unknown University")

st.header(f"{university} Budget Plan Details")

st.divider()

plan_data = {
    "KU Leuven": [
        {"Program": "Computer Science", "Current Target": "18% -> 11%", "Budget Adj.": "4.34M", "Status": "Overfunded"},
        {"Program": "Engineering", "Current Target": "15% -> 10%", "Budget Adj.": "3.21M", "Status": "Overfunded"},
        {"Program": "Business", "Current Target": "12% -> 8%", "Budget Adj.": "2.45M", "Status": "Overfunded"}

    ], 
    "Ghent University": [
        {"Program": "Computer Science", "Current Target": "20% -> 12%", "Budget Adj.": "5.12M", "Status": "Overfunded"},
        {"Program": "Engineering", "Current Target": "18% -> 10%", "Budget Adj.": "4.56M", "Status": "Overfunded"},
        {"Program": "Business", "Current Target": "15% -> 9%", "Budget Adj.": "3.78M", "Status": "Overfunded"}
    ],
    'Université Libre de Bruxelles (ULB)': [
        {"Program": "Computer Science", "Current Target": "22% -> 14%", "Budget Adj.": "6.23M", "Status": "Overfunded"},
        {"Program": "Engineering", "Current Target": "20% -> 12%", "Budget Adj.": "5.67M", "Status": "Overfunded"}
    ]
}

with st.container(border=True):
    st.subheader("Program Reallocation Table")
    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    col1.write("**Program**")
    col2.write("**Current Target**")
    col3.write("**Budget Adj.**")
    col4.write("**Status**")

    st.divider()

    rows = plan_data.get(university, [])

    for row in rows:
        with st.container():
            col1, col2, col3, col4 = st.columns(4)
            col1.write(row["Program"])
            col2.write(row["Current Target"])
            col3.write(row["Budget Adj."])
            col4.write(row["Status"])







