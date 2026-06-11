import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests

from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

API = 'http://web-api:4000'

st.title("Labor Statistician Portal")

# Same for every statistician (it's the role, not the person), so these are
# constants. Name + email come from the picked DB user.
ROLE_INFO = {
    'title': 'Labor Market Statistician',
    'organization': 'Eurostat, Directorate for Social Statistics',
    'region': 'EU27',
    'focus': 'Employment trends & education-to-work transitions',
}


@st.cache_data(ttl=300)
def load_statisticians():
    r = requests.get(f'{API}/labor/statisticians', timeout=10)
    r.raise_for_status()
    return r.json()


try:
    people = load_statisticians()
except Exception as e:
    logger.error(f'Could not load statisticians: {e}')
    st.error(f'Could not reach the labor API: {e}')
    st.stop()

if not people:
    st.warning('No statisticians found in the database.')
    st.stop()

# Pick a user. If one was already chosen (here or on Home), keep it selected.
names = {f"{p['first_name']} {p['last_name']}": p for p in people}
labels = list(names.keys())
prior = st.session_state.get('selected_statistician')
prior_label = prior and f"{prior['first_name']} {prior['last_name']}"
start = labels.index(prior_label) if prior_label in names else 0

choice = st.selectbox('Select statistician', labels, index=start)
selected = names[choice]
st.session_state['selected_statistician'] = selected

st.header(f"Welcome {selected['first_name']}")
st.divider()

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Name:** {selected['first_name']} {selected['last_name']}")
    st.write(f"**Email:** {selected['email']}")
    st.write(f"**Title:** {ROLE_INFO['title']}")
with col2:
    st.write(f"**Organization:** {ROLE_INFO['organization']}")
    st.write(f"**Region:** {ROLE_INFO['region']}")
    st.write(f"**Focus:** {ROLE_INFO['focus']}")

st.divider()

st.write("Pick where you'd like to go:")
col1, col2 = st.columns(2)
with col1:
    if st.button('Run Predictions', type='primary', use_container_width=True):
        st.switch_page('pages/10_Labor_Statistician_Home.py')
with col2:
    if st.button('Explore the Data', use_container_width=True):
        st.switch_page('pages/11_Labor_Statistician_Charts.py')

st.divider()