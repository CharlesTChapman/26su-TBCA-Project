import logging
logger = logging.getLogger(__name__)

import streamlit as st
from datetime import date, time
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')

SideBarLinks()

st.title("All Pros and Cons")

with st.container(border = True):
        st.subheader("Pros and Cons")
        st.divider()
        pros_col, cons_col = st.columns(2)
        with pros_col:
            st.write("**Pros**")
            st.write("- Large research output")
            st.write("- Low tuition")
            st.write("- Strong CS Program")

        with cons_col:
            st.write("**Cons**")
            st.write("- Competitive admissions")
            st.write("- Limited English Programs")
            st.write("- High cost of living")
