# Idea borrowed from https://github.com/fsmosca/sample-streamlit-authenticator

# This file has functions to add links to the left sidebar based on the user's role.

import streamlit as st


# ---- General ----------------------------------------------------------------

def home_nav():
    st.sidebar.page_link("Home.py", label="Home", icon="🏠")


def about_page_nav():
    st.sidebar.page_link("pages/30_About.py", label="About", icon="🧠")


# ---- Role: student ----------------------------------------------------------

def student_home_nav():
    st.sidebar.page_link(
        "pages/00_Student_Home.py", label="Student Home", icon="🏠"
    )


def student_survey_nav():
    st.sidebar.page_link(
        "pages/01_Student_Survey.py", label="Student Survey", icon="📝"
    )


def student_portal_nav():
    st.sidebar.page_link(
        "pages/02_Student_Data.py", label="My Portal", icon="🎓"
    )


def student_recommendations_nav():
    st.sidebar.page_link(
        "pages/03_Student_Data_Universities_List.py", label="University Recommendations", icon="🏫"
    )


def student_pros_cons_nav():
    st.sidebar.page_link(
        "pages/04_Student_Data_All_Pros_Cons.py", label="Pros & Cons", icon="⚖️"
    )


def student_favorites_nav():
    st.sidebar.page_link(
        "pages/05_Student_Data_All_Favorites.py", label="Favorites", icon="⭐"
    )


def student_user_info_nav():
    st.sidebar.page_link(
        "pages/07_Student_Data_User_Information.py", label="User Information", icon="👤"
    )


# ---- Role: labor_statistician -----------------------------------------------

def labor_statistician_home_nav():
    st.sidebar.page_link(
        "pages/10_Labor_Statistician_Home.py", label="Labor Statistician Home", icon="📊"
    )


def labor_statistician_charts_nav():
    st.sidebar.page_link(
        "pages/11_Labor_Statistician_Charts.py", label="Explore the Data", icon="📈"
    )


# ---- Role: budget_manager ---------------------------------------------------

def budget_manager_home_nav():
    st.sidebar.page_link(
        "pages/20_Budget_Manager_Home.py", label="Budget Manager Home", icon="💰"
    )


# ---- Sidebar assembly -------------------------------------------------------

def SideBarLinks(show_home=False):
    """
    Renders sidebar navigation links based on the logged-in user's role.
    The role is stored in st.session_state when the user logs in on Home.py.
    Every page in the active role's section is shown, so the user can move
    freely between them. Click-through detail pages (e.g. a single university
    or budget plan) are intentionally left out since they need a prior
    selection to render.
    """

    # Logo appears at the top of the sidebar on every page
    st.sidebar.image("assets/logo.png", width=150)

    # If no one is logged in, send them to the Home (login) page
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.switch_page("Home.py")

    # Home link is shown on every page
    home_nav()

    if st.session_state["authenticated"]:

        if st.session_state["role"] == "student":
            student_home_nav()
            student_survey_nav()
            student_portal_nav()
            student_recommendations_nav()
            student_pros_cons_nav()
            student_favorites_nav()
            student_user_info_nav()

        if st.session_state["role"] == "labor_statistician":
            labor_statistician_home_nav()
            labor_statistician_charts_nav()

        if st.session_state["role"] == "budget_manager":
            budget_manager_home_nav()

    # About link appears at the bottom for all roles
    about_page_nav()

    if st.session_state["authenticated"]:
        if st.sidebar.button("Logout"):
            del st.session_state["role"]
            del st.session_state["authenticated"]
            st.switch_page("Home.py")
