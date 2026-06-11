import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

BIOS = {
    "Tyler": {
        "image": "assets/dev_headshots/tyler_gladu_headshot.png",
        "role": "Database Design & Front End",
        "bio": """Hi! My name is Tyler Gladu and I am from Upton, MA. 
                I helped build our user interface, 
                create routes in our API layer, and develop our database to store information.
                I helped build around 75% of our UI and 40% of our API layer, to allow our frontend to communicate
                 with our backend. """,
        "linkedin": "https://www.linkedin.com/in/tyler-gladu-bb7783239/",
    },
    "Charlie": {
        "image": "assets/dev_headshots/charles_chapman_headshot.png",
        "role": "Database Design & Front End",
        "bio": "Charlie led database design and implementation and contributed to "
               "the front end and user interface.",
        "linkedin": "https://www.linkedin.com/in/charlestchapman/",
    },
    "Bina": {
        "image": "assets/dev_headshots/bina_bakhramova_headshot.png",
        "role": "Machine Learning & Backend",
        "bio": "Bina built the machine learning models powering the platform's "
               "predictions, along with a large portion of the logic and backend.",
        "linkedin": "https://www.linkedin.com/in/binafsha-bakhramova-616637267/",
    },
    "Alyssa": {
        "image": "assets/dev_headshots/alyssa_haidar_headshot.png",
        "role": "Machine Learning & Backend",
        "bio": "Alyssa built the machine learning models powering the platform's "
               "predictions, along with a large portion of the logic and backend.",
        "linkedin": "https://www.linkedin.com/in/alyssa-haidar-21662a246/",
    },
}

name = st.session_state.get("selected_member")

if name is None or name not in BIOS:
    st.warning("No team member selected.")
    if st.button("Back to About"):
        st.switch_page("pages/30_About.py")
    st.stop()

member = BIOS[name]

col_img, col_text = st.columns([1, 2])
with col_img:
    st.image(member["image"], use_container_width=True)
with col_text:
    name_col, link_col = st.columns([3, 1], vertical_alignment="center")
    with name_col:
        st.title(name)
    with link_col:
        st.link_button("LinkedIn", member["linkedin"], icon=":material/link:")
    st.caption(member["role"])
    st.write(member["bio"])

st.divider()

if st.button("Back to About", type="primary"):
    st.switch_page("pages/30_About.py")
