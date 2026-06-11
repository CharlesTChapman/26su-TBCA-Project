import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

col1, col2 = st.columns([6,1])

with col1:
    st.title('EU Labor Market Explorer')
    st.caption('Eurostat EU27 · 2013–2023')
with col2:
    st.write("")
    st.write("")
    if st.button("Explore the Data", type='primary'):
        st.switch_page("pages/11_Labor_Statistician_Charts.py")

API = 'http://web-api:4000'

@st.cache_data(ttl=300)
def load_observations():
    r = requests.get(f'{API}/labor/observations')
    r.raise_for_status()
    return pd.DataFrame(r.json())

try:
    df = load_observations()
except Exception as e:
    st.error(f'Could not reach API: {e}')
    st.stop()

COUNTRY_NAMES = {
    'AT': 'Austria', 
    'BE': 'Belgium',
    'BG': 'Bulgaria', 
    'CY': 'Cyprus',
    'CZ': 'Czech Republic', 
    'DE': 'Germany', 
    'DK': 'Denmark', 
    'EE': 'Estonia',
    'EL': 'Greece', 
    'ES': 'Spain', 
    'FI': 'Finland', 
    'FR': 'France',
    'HR': 'Croatia', 
    'HU': 'Hungary', 
    'IE': 'Ireland', 
    'IT': 'Italy',
    'LT': 'Lithuania', 
    'LU': 'Luxembourg', 
    'LV': 'Latvia', 
    'MT': 'Malta',
    'NL': 'Netherlands', 
    'PL': 'Poland', 
    'PT': 'Portugal', 
    'RO': 'Romania',
    'SE': 'Sweden', 
    'SI': 'Slovenia', 
    'SK': 'Slovakia'
}

sectors   = sorted(df['sector'].unique())
countries = sorted(df['geo'].unique())



# ── prediction widget ─────────────────────────────────────────
st.subheader('Run a Prediction')
st.caption('Select a country and sector — values are pulled from the most recent year in the data.')



col1, col2 = st.columns(2)

with col1:
    st.markdown('**Model 1: Employment Level**')
    m1_country = st.selectbox('Country', countries, format_func = COUNTRY_NAMES.get, key = 'm1_country') #type: ignore
    
    m1_sector  = st.selectbox('Sector', sectors, key='m1_sector')

    # auto-fill lag from most recent row for that country/sector
    m1_row = df[(df['geo'] == m1_country) & (df['sector'] == m1_sector)].sort_values('time').iloc[-1] if len(df[(df['geo'] == m1_country) & (df['sector'] == m1_sector)]) > 0 else None
    m1_default_lag = float(m1_row['employment_thousands']) if m1_row is not None else 715.0

    emp_lag = st.number_input("Last year's employment (thousands)",
                               min_value=0.0, value=m1_default_lag, step=10.0, key='m1_lag')
    if st.button('Predict Level', type='primary'):
        r = requests.get(f'{API}/labor/predict/level/{emp_lag}')
        result = r.json()
        st.metric('Predicted Employment (thousands)', f"{result['predicted_employment_thousands']:,.2f}")

with col2:
    st.markdown('**Model 2: Employment Change**')
    m2_country = st.selectbox('Country', countries, format_func = COUNTRY_NAMES.get, key = 'm2_country') #type: ignore
    m2_sector  = st.selectbox('Sector', sectors, key='m2_sector')

    # auto-fill from most recent row
    m2_row = df[(df['geo'] == m2_country) & (df['sector'] == m2_sector)].sort_values('time').iloc[-1] if len(df[(df['geo'] == m2_country) & (df['sector'] == m2_sector)]) > 0 else None
    m2_default_grads = float(m2_row['graduates']) if m2_row is not None else 20000.0
    m2_default_lag   = float(m2_row['employment_thousands']) if m2_row is not None else 715.0

    grads = st.number_input('Graduates entering sector',
                             min_value=0.0, value=m2_default_grads, step=500.0, key='m2_grads')
    lag2  = st.number_input('Prior employment (thousands)',
                             min_value=0.0, value=m2_default_lag, step=10.0, key='m2_lag')
    year  = st.number_input('Year', min_value=2013, max_value=2030, value=2024, step=1, key='m2_year')

    if st.button('Predict Change', type='primary'):
        r = requests.get(f'{API}/labor/predict/change/{grads}/{lag2}/{int(year)}')
        result = r.json()
        val = result['predicted_change_thousands']
        st.metric('Predicted Change (thousands)', f"{val:+,.2f}")

st.divider()


