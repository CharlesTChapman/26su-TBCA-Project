#### MAIN ENTRYPOINT FOR APP ####

# Set up logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
import time
import requests
from modules.nav import SideBarLinks

# Base URL for the REST API
API = 'http://web-api:4000'


@st.cache_data(ttl=300)
def load_students():
    """Fetch all students from the API's GET /students route."""
    r = requests.get(f'{API}/students')
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=300)
def load_labor_statisticians():
    """Fetch all labor statisticians from the API's GET /labor_statisticians route."""
    r = requests.get(f'{API}/labor_statisticians')
    r.raise_for_status()
    return r.json()


@st.cache_data(ttl=300)
def load_budget_managers():
    """Fetch all budget managers from the API's GET /budget_managers route."""
    r = requests.get(f'{API}/budget_managers')
    r.raise_for_status()
    return r.json()


def _load(loader, label):
    """Run a loader, logging and surfacing any API error and returning []."""
    try:
        return loader()
    except Exception as e:
        logger.error(f"Could not load {label} from API: {e}")
        st.error(f"Could not load {label} from the API: {e}")
        return []


# Load the people for each persona from the database
students = _load(load_students, "students")
labor_statisticians = _load(load_labor_statisticians, "labor statisticians")
budget_managers = _load(load_budget_managers, "budget managers")

# wide streamlit layout
st.set_page_config(layout='wide')

# Users on this page are not yet authenticated
st.session_state['authenticated'] = False

SideBarLinks(show_home=True)

# Rotating text that transitions through a list of titles
NAMES = [
    "The Best Choice Academics 🎓   ",
    "Think Before Committing Analytics 📊   ",
    "True Budget Clarity Accounting 💶   ",
]

@st.fragment(run_every="5s")
def rotating_banner():
    idx = int(time.time() // 5) % len(NAMES)
    text = NAMES[idx]
    n = len(text)
    # Emphasize the T/B/C/A letters
    html = "".join(
        f'<span class="tbca">{c}</span>' if c.isupper() else c for c in text
    )
    st.markdown(
        f"""
        <style>
        .rotating-text {{
            display: inline-block;
            white-space: nowrap;
            overflow: hidden;
            font-size: 2.75rem;
            font-weight: 700;
            line-height: 1.2;
            color: #dfe3ee;
            width: {n}ch;
            animation: type 1.4s steps({n}, end);
        }}
        .rotating-text .tbca {{
            color: #5b86e0;
            font-weight: 900;
        }}
        @keyframes type  {{ from {{ width: 0; }} to {{ width: {n}ch; }} }}
        </style>
        <div class="rotating-text" key="{idx}">{html}</div>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------------------------------------------------------
# PAGE CONTENT
# -----------------------------------------------------------------------------

logger.info("Loading the Home page of the app")
rotating_banner()
st.subheader("Who would you like to log in as?")

st.divider()

st.write("Select one of the following user personas:")

col1, col2, col3 = st.columns(3)

# Users mimic logging in by selecting their account from a list of all accounts
with col1:
    st.subheader("Student")
    st.caption("Browse universities, compare tuition costs, and explore programs across Europe.")
    if students:
        student_options = {
            f"{s['first_name']} {s['last_name']} ({s['email']})": s
            for s in students
        }

        selected_label = st.selectbox(
            "Select a student",
            options=list(student_options.keys()),
            index=None,
            placeholder="Choose a student...",
        )

        if selected_label:
            selected_student = student_options[selected_label]
            st.session_state['selected_student'] = selected_student
    else:
        st.info("No students available to choose from.")

    if st.button(f'Log in as {st.session_state.get("selected_student", {}).get("first_name", "Student")}',
                type='primary',
                use_container_width=True):
        # when user clicks the button, they are now considered authenticated
        st.session_state['authenticated'] = True
        # set the role of the current user
        st.session_state['role'] = 'student'
        # add the first name of the user (so it can be displayed on subsequent pages).
        st.session_state['first_name'] = st.session_state.get('selected_student', {}).get('first_name', 'Student')
        # switch to the next page
        logger.info("Logging in as Student Persona")
        st.switch_page('pages/00_Student_Home.py')

with col2:
    st.subheader("Labor Statistician")
    st.caption("Analyze employment trends, track labor market data, and generate insights across industries.")
    if labor_statisticians:
        statistician_options = {
            f"{s['first_name']} {s['last_name']} ({s['email']})": s
            for s in labor_statisticians
        }

        selected_statistician_label = st.selectbox(
            "Select a labor statistician",
            options=list(statistician_options.keys()),
            index=None,
            placeholder="Choose a labor statistician...",
        )

        if selected_statistician_label:
            selected_statistician = statistician_options[selected_statistician_label]
            st.session_state['selected_statistician'] = selected_statistician
    else:
        st.info("No labor statisticians available to choose from.")

    if st.button(f'Log in as {st.session_state.get("selected_statistician", {}).get("first_name", "Labor Statistician")}',
                type='primary',
                use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'labor_statistician'
        st.session_state['first_name'] = st.session_state.get('selected_statistician', {}).get('first_name', 'Labor Statistician')
        logger.info("Logging in as Labor Statistician Persona")
        st.switch_page('pages/10_Labor_Statistician_Home.py')
with col3:
    st.subheader("Budget Manager")
    st.caption("Monitor university budgets, review financial allocations, and track spending across programs.")
    if budget_managers:
        manager_options = {
            f"{s['first_name']} {s['last_name']} ({s['email']})": s
            for s in budget_managers
        }

        selected_manager_label = st.selectbox(
            "Select a budget manager",
            options=list(manager_options.keys()),
            index=None,
            placeholder="Choose a budget manager...",
        )

        if selected_manager_label:
            selected_manager = manager_options[selected_manager_label]
            st.session_state['selected_manager'] = selected_manager
    else:
        st.info("No budget managers available to choose from.")

    if st.button(f'Log in as {st.session_state.get("selected_manager", {}).get("first_name", "Budget Manager")}',
                type='primary',
                use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'budget_manager'
        st.session_state['first_name'] = st.session_state.get('selected_manager', {}).get('first_name', 'Budget Manager')
        logger.info("Logging in as Budget Manager Persona")
        st.switch_page('pages/20_Budget_Manager_Home.py')