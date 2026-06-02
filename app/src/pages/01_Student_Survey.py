import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("Student Survey")
st.write(
    "This is a demo page showcasing every Streamlit question/input type. "
    "Fill it out and submit to see the collected responses."
)

# A form batches all widgets and only triggers a rerun on submit, so the
# page does not refresh on every individual interaction.
with st.form("student_survey", clear_on_submit=False):

    # ---- Majors -------------------------------------------------------------
    st.subheader("Which majors are you interested in?")
    majors = st.multiselect(
        "Multi-select — which topics interest you?",
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
    campus_size = st.slider("How large of a campus do you prefer? (Student population)",
                             min_value=100, max_value=50000, value=(5000, 15000), step=500,
                             help="The size of the campus in terms of student population")
    
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
    responses = {
        "majors": majors,
        "country": country,
        "proximity_km": list(proximity),
        "campus_type": campus_type,
        "campus_size": list(campus_size),
        "budget_usd": budget,
        "financial_aid": financial_aid,
    }
    st.success("Thanks for completing the survey! Here are your responses:")
    st.json(responses)
