import logging

import streamlit as st
import requests
import pandas as pd

from modules.nav import SideBarLinks

logger = logging.getLogger(__name__)

st.set_page_config(layout='wide')
SideBarLinks()

col1, col2 = st.columns([6, 1])
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
    'AT': 'Austria', 'BE': 'Belgium', 'BG': 'Bulgaria', 'CY': 'Cyprus',
    'CZ': 'Czech Republic', 'DE': 'Germany', 'DK': 'Denmark', 'EE': 'Estonia',
    'EL': 'Greece', 'ES': 'Spain', 'FI': 'Finland', 'FR': 'France',
    'HR': 'Croatia', 'HU': 'Hungary', 'IE': 'Ireland', 'IT': 'Italy',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MT': 'Malta',
    'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
    'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia',
}

sectors = sorted(df['sector'].unique())
countries = sorted(df['geo'].unique())

st.subheader('Run a Prediction')
st.caption('Pick a country and sector once. Inputs auto-fill from the most recent '
           'year, then both models run and combine into a single estimate.')

col1, col2 = st.columns(2)
with col1:
    pred_country = st.selectbox('Country', countries,
                                format_func=COUNTRY_NAMES.get, key='pred_country')  # type: ignore
with col2:
    pred_sector = st.selectbox('Sector', sectors, key='pred_sector')


match = df[(df['geo'] == pred_country) & (df['sector'] == pred_sector)].sort_values('time')
row = match.iloc[-1] if len(match) else None
default_lag = float(row['employment_thousands']) if row is not None else 715.0
default_grads = float(row['graduates']) if row is not None and pd.notna(row['graduates']) else 20000.0
default_year = min(max(int(row['time']) + 1, 2013), 2030) if row is not None else 2024

c1, c2, c3 = st.columns(3)
with c1:
    emp_lag = st.number_input("Last year's employment (thousands)",
                              min_value=0.0, value=default_lag, step=10.0, key='emp_lag')
with c2:
    grads = st.number_input('Graduates entering sector',
                            min_value=0.0, value=default_grads, step=500.0, key='grads')
with c3:
    year = st.number_input('Year', min_value=2013, max_value=2030,
                           value=default_year, step=1, key='year')

if st.button('Run Prediction', type='primary'):
    try:
        lvl_resp = requests.get(f'{API}/labor/predict/level/{emp_lag}', timeout=10)
        lvl_resp.raise_for_status()
        chg_resp = requests.get(
            f'{API}/labor/predict/change/{grads}/{emp_lag}/{int(year)}', timeout=10)
        chg_resp.raise_for_status()
    except Exception as e:
        logger.error(f'Prediction failed: {e}')
        st.error(f'Prediction failed: {e}')
    else:
        level = lvl_resp.json()['predicted_employment_thousands']
        change = chg_resp.json()['predicted_change_thousands']

        model1_pred = level
        model2_pred = emp_lag + change
        combined = (model1_pred + model2_pred) / 2
        delta = combined - emp_lag

        country_label = COUNTRY_NAMES.get(pred_country, pred_country)
        st.metric(
            'Predicted employment next year (thousands)',
            f"{combined:,.1f}",
            delta=f"{delta:+,.1f}",
        )
        st.caption(
            f"Predicted employment for {country_label} / {pred_sector} next year, "
            f"The arrow is the change from last year "
            f"({emp_lag:,.1f}k): green means the sector is growing, red means "
            f"it's shrinking."
        )

st.divider()