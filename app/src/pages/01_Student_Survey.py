import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks
import requests

st.set_page_config(layout='wide')

SideBarLinks()

API = "http://web-api:4000"

degree_map = {"Bachelor's Degree": 1,
              "Master's Degree": 2, 
              "Doctorate's Degree": 3}

size_map = {"Small (<5,000 students)": 1,
            "Medium (5,000-15,000 students)": 2, 
            "Large (>15,000 students)": 3}

st.title("Student Survey")


# A form batches all widgets and only triggers a rerun on submit, so the
# page does not refresh on every individual interaction.
with st.form("student_survey", clear_on_submit=False):

    # ---- Majors -------------------------------------------------------------
    st.subheader("Degree Preferences")
    majors = st.selectbox(
        "Which major are you interested in?",
        options=["Accounting", "Anthropology", "Architecture", "Art", "Biology",
                 "Business", "Chemistry", "Communications", "Computer Science",
                 "Criminal Justice", "Data Science", "Design", "Economics",
                 "Education", "Engineering", "English", "Environmental Science",
                 "Finance", "History", "Information Technology", "Journalism",
                 "Kinesiology", "Law", "Linguistics", "Management", "Marketing",
                 "Mathematics", "Mechanical Engineering", "Music", "Nursing",
                 "Philosophy", "Physics", "Political Science", "Psychology",
                 "Public Health", "Religious Studies", "Sociology", "Statistics",
                 "Theater"],
    )

    degree_level = st.radio("What degree do you want to finish with?",
                            options = ["Bachelor's Degree", "Master's Degree", "Doctorate's Degree"])

    # ---- Location preferences -----------------------------------------------
    st.subheader("Location Preferences")
    country = st.text_input("What country do you live in?",
                               placeholder="Enter your country")
    proximity = st.slider("How far from home would you like to study? (km)",
                             min_value=0, max_value=1500, value=(300, 1000), step=50,
                             help="Distance in kilometers from your home location")
    
    # ---- Campus preferences -------------------------------------------------
    st.subheader("Campus Preferences")
    campus_type = st.selectbox("What type of campus do you prefer?",
                               options=["Urban", "Suburban", "Rural"],
                               help="The setting of the campus")
    #campus_size = st.slider("How large of a campus do you prefer? (Student population)",
     #                        min_value=100, max_value=50000, value=(5000, 15000), step=500,
     #                        help="The size of the campus in terms of student population")

    campus_size = st.radio("What size campus would you prefer?", 
                            options =["Small (<5,000 students)", "Medium (5,000-15,000 students)", "Large (>15,000 students)"])

    
    # ---- Financial preferences ----------------------------------------------
    st.subheader("Financial Preferences")
    budget = st.number_input("What is your budget for tuition per year? ($)",
                             min_value=0, max_value=100000, value=20000, step=1000,
                             help="Your budget for annual tuition in USD")
    financial_aid = st.toggle("Are you interested in financial aid?",
                             help="Toggle if you are interested in receiving financial aid")

    submitted = st.form_submit_button("Submit Survey", type="primary",
                                      use_container_width=True)

# ---- Results ----------------------------------------------------------------
if submitted:
    student_id = st.session_state.get('student_id')

    survey_data = {
        "student_budget": float(budget),
        "student_degree_level": degree_map[degree_level],
        "student_size": size_map[campus_size]
    }

    # Check if survey already exists
    check = requests.get(f"{API}/survey_form/{student_id}", timeout=10)

    if check.status_code == 200:
        response = requests.put(f"{API}/survey_form/{student_id}", json=survey_data, timeout=20)
    else:
        response = requests.post(f"{API}/survey_form/{student_id}", json=survey_data, timeout=20)

    if response.status_code in (200, 201):
        st.session_state["survey_responses"] = {
            "majors": majors,
            "degree_level": degree_level,
            "country": country,
            "proximity_km": list(proximity),
            "campus_type": campus_type,
            "campus_size": campus_size,
            "budget_usd": budget,
            "financial_aid": financial_aid,
        }
        st.switch_page("pages/02_Student_Data.py")
    else:
        st.error("Failed to submit survey. Please try again.")