import streamlit as st
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.write("# About Us")

st.markdown(
    """
    We're four computer science students at Northeastern University building tools to make European higher education data more accessible and useful. Tyler and Charlie led database design and implementation and contributed to the front end and user interface. Alyssa and Bina built the machine learning models powering the platform's predictions, along with a large portion of the logic and backend.
    """
)

st.write("## Meet the Team")

team = [
    {"name": "Tyler", "image": "assets/dev_headshots/tyler_gladu_headshot.png"},
    {"name": "Charlie", "image": "assets/dev_headshots/charles_chapman_headshot.png"},
    {"name": "Bina", "image": "assets/dev_headshots/bina_bakhramova_headshot.png"},
    {"name": "Alyssa", "image": "assets/dev_headshots/alyssa_haidar_headshot.png"},
]

cols = st.columns(len(team))
for col, member in zip(cols, team):
    with col:
        st.subheader(member["name"])
        st.image(member["image"], use_container_width=True)
        if st.button(f"View {member['name']}'s Profile",
                     key=member["name"],
                     use_container_width=True):
            st.session_state["selected_member"] = member["name"]
            st.switch_page("pages/31_Team_Bio.py")

if st.button("Return to Home", type="primary"):
    st.switch_page("Home.py")
