##################################################
# This is the main/entry-point file for the
# sample application for your project
##################################################

# Set up basic logging infrastructure
import logging
logging.basicConfig(format='%(filename)s:%(lineno)s:%(levelname)s -- %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# import the main streamlit library as well
# as SideBarLinks function from src/modules folder
import streamlit as st
from modules.nav import SideBarLinks

# streamlit supports regular and wide layout (how the controls
# are organized/displayed on the screen).
st.set_page_config(layout='wide')

# If a user is at this page, we assume they are not
# authenticated.  So we change the 'authenticated' value
# in the streamlit session_state to false.
st.session_state['authenticated'] = False

# Use the SideBarLinks function from src/modules/nav.py to control
# the links displayed on the left-side panel.
# IMPORTANT: ensure src/.streamlit/config.toml sets
# showSidebarNavigation = false in the [client] section
SideBarLinks(show_home=True)

# ***************************************************
#    The major content of this page
# ***************************************************




logger.info("Loading the Home page of the app")
st.title("🎓 TBCAcademics")
st.subheader("Who would you like to log in as?")

st.divider()


        
st.write("Select one of the following user personas:")


col1, col2, col3 = st.columns(3)


# For each of the user personas for which we are implementing
# functionality, we put a button on the screen that the user
# can click to MIMIC logging in as that mock user.
with col1:
    st.subheader("Student Portal")
    st.caption("Student")
    st.write("Browse universities, compare tuition costs, and explore programs across Europe.")

    if st.button('Log in as a Student',
                type='primary',
                use_container_width=True):
        # when user clicks the button, they are now considered authenticated
        st.session_state['authenticated'] = True
        # we set the role of the current user
        st.session_state['role'] = 'student'
        # we add the first name of the user (so it can be displayed on
        # subsequent pages).
        st.session_state['first_name'] = 'Student'
        # finally, we ask streamlit to switch to another page, in this case, the
        # landing page for this particular user type
        logger.info("Logging in as Student Persona")
        st.switch_page('pages/00_Student_Home.py')

with col2:
    st.subheader("Cher")
    st.caption("Labor Statistician")
    st.write("Analyze employment trends, track labor market data, and generate insights across industries.")

    if st.button('Log in as Cher',
                type='primary',
                use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'labor_statistician'
        st.session_state['first_name'] = 'Cher'
        logger.info("Logging in as Labor Statistician Persona")
        st.switch_page('pages/10_Labor_Statistician_Home.py')
with col3:
    st.subheader("Zuhal")
    st.caption("Budget Manager")
    st.write("Monitor university budgets, review financial allocations, and track spending across programs.")

    if st.button('Log in as Zuhal',
                type='primary',
                use_container_width=True):
        st.session_state['authenticated'] = True
        st.session_state['role'] = 'budget_manager'
        st.session_state['first_name'] = 'Zuhal'
        logger.info("Logging in as Budget Manager Persona")
        st.switch_page('pages/20_Budget_Manager_Home.py')