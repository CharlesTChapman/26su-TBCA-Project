import logging
logger = logging.getLogger(__name__)

import streamlit as st
import requests
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modules.nav import SideBarLinks

st.set_page_config(layout='wide')
SideBarLinks()

st.title('EU Labor Market Explorer')
st.caption('Eurostat EU27 · 2013–2023')

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

# sidebar filters
st.sidebar.header('Filters')
countries = sorted(df['geo'].unique())
sectors   = sorted(df['sector'].unique())
selected_countries = st.sidebar.multiselect('Countries', countries, default=countries)
selected_sectors   = st.sidebar.multiselect('Sectors', sectors, default=sectors)

filtered = df[
    df['geo'].isin(selected_countries) &
    df['sector'].isin(selected_sectors)
]

# ── prediction widget ─────────────────────────────────────────
st.subheader('Run a Prediction')
st.caption('Select a country and sector — values are pulled from the most recent year in the data.')

col1, col2 = st.columns(2)

with col1:
    st.markdown('**Model 1: Employment Level**')
    m1_country = st.selectbox('Country', countries, key='m1_country')
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
    m2_country = st.selectbox('Country', countries, key='m2_country')
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

# ── charts ────────────────────────────────────────────────────
st.subheader('Explore the Data')

NUMERIC_COLS = ['employment_thousands', 'graduates', 'emp_change',
                'employment_rate', 'grad_ratio', 'absorption_rate', 'predicted']
LABEL_MAP = {
    'employment_thousands': 'Employment (thousands)',
    'graduates':            'Graduates',
    'emp_change':           'Employment Change',
    'employment_rate':      'Employment Rate',
    'grad_ratio':           'Grad Ratio',
    'absorption_rate':      'Absorption Rate',
    'predicted':            'Predicted Employment',
}

tab1, tab2, tab3, tab4 = st.tabs(['Employment Trend', 'Country Comparison', 'Absorption Rate', 'Custom Scatter'])

with tab1:
    t1_y = st.selectbox('Y axis', NUMERIC_COLS,
                         format_func=lambda c: LABEL_MAP[c], key='t1_y')
    trend = filtered.groupby(['time','sector'])[t1_y].sum().reset_index()
    fig1 = px.line(trend, x='time', y=t1_y, color='sector', markers=True,
                   labels={'time':'Year', t1_y: LABEL_MAP[t1_y], 'sector':'Sector'})
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    t2_y = st.selectbox('Metric', NUMERIC_COLS,
                         format_func=lambda c: LABEL_MAP[c], key='t2_y')
    latest_year = int(df['time'].max())
    latest = df[df['time'] == latest_year].groupby('geo', as_index=False).agg(
        val=(t2_y, 'mean')
    )
    latest = latest[latest['geo'].isin(selected_countries)].sort_values('val')
    fig2 = px.bar(latest, x='val', y='geo', orientation='h',
                  color='val', color_continuous_scale='Teal',
                  title=f'{LABEL_MAP[t2_y]} by Country ({latest_year})',
                  labels={'val': LABEL_MAP[t2_y], 'geo':'Country'})
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    absorption = filtered.groupby('sector')['absorption_rate'].median().reset_index().sort_values('absorption_rate')
    fig3 = px.bar(absorption, x='absorption_rate', y='sector', orientation='h',
                  color='absorption_rate', color_continuous_scale=['red','green'],
                  labels={'absorption_rate':'Median New Jobs per Prior-Year Graduate','sector':'Sector'})
    fig3.add_vline(x=0, line_color='black', line_width=1)
    st.plotly_chart(fig3, use_container_width=True)
    st.caption('Positive = sector absorbs more workers than graduates produced. Negative = graduate surplus.')

with tab4:
    c1, c2, c3 = st.columns(3)
    with c1:
        t4_x = st.selectbox('X axis', NUMERIC_COLS,
                              format_func=lambda c: LABEL_MAP[c],
                              index=0, key='t4_x')
    with c2:
        t4_y = st.selectbox('Y axis', NUMERIC_COLS,
                              format_func=lambda c: LABEL_MAP[c],
                              index=6, key='t4_y')
    with c3:
        t4_color = st.selectbox('Color by', ['sector','geo'], key='t4_color')

    fig4 = px.scatter(filtered, x=t4_x, y=t4_y, color=t4_color,
                      opacity=0.55, hover_data=['geo','time','sector'],
                      labels={t4_x: LABEL_MAP[t4_x], t4_y: LABEL_MAP[t4_y]})
    st.plotly_chart(fig4, use_container_width=True)
