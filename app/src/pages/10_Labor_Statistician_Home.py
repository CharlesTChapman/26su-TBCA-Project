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
 
# sidebar
st.sidebar.header('Filters')
countries = sorted(df['geo'].unique())
sectors   = sorted(df['sector'].unique())
selected_countries = st.sidebar.multiselect('Countries', countries, default=['DE','FR','PL'])
selected_sectors   = st.sidebar.multiselect('Sectors', sectors, default=sectors)
 
filtered = df[
    df['geo'].isin(selected_countries) &
    df['sector'].isin(selected_sectors)
]
 
# prediction widget
st.subheader('Run a Prediction')
col1, col2 = st.columns(2)
 
with col1:
    st.markdown('**Model 1: Employment Level**')
    emp_lag = st.number_input("Last year's employment (thousands)", min_value=0.0, value=715.0, step=10.0)
    if st.button('Predict Level', type='primary'):
        r = requests.get(f'{API}/labor/predict/level/{emp_lag}')
        st.metric('Predicted Employment (thousands)', r.json()['predicted_employment_thousands'])
 
with col2:
    st.markdown('**Model 2: Employment Change**')
    grads = st.number_input('Graduates entering sector', min_value=0.0, value=20000.0, step=500.0)
    lag2  = st.number_input("Prior employment (thousands)", min_value=0.0, value=715.0, step=10.0)
    year  = st.number_input('Year', min_value=2013, max_value=2030, value=2024, step=1)
    if st.button('Predict Change', type='primary'):
        r = requests.get(f'{API}/labor/predict/change/{grads}/{lag2}/{int(year)}')
        st.metric('Predicted Change (thousands)', r.json()['predicted_change_thousands'])
 
st.divider()
 
# charts in tabs
tab1, tab2, tab3, tab4 = st.tabs(['Employment Trend', 'Country Rates', 'Absorption Rate', 'Model Fit'])
 
with tab1:
    trend = filtered.groupby(['time','sector'])['employment_thousands'].sum().reset_index()
    fig1 = px.line(trend, x='time', y='employment_thousands', color='sector', markers=True,
                   labels={'time':'Year','employment_thousands':'Employment (thousands)','sector':'Sector'})
    st.plotly_chart(fig1, use_container_width=True)
 
with tab2:
    latest_year = int(df['time'].max())
    latest = df[df['time'] == latest_year].groupby('geo', as_index=False).agg(
        emp_rate=('employment_rate', 'mean')
    )
    latest = latest[latest['geo'].isin(selected_countries)].sort_values('emp_rate')
    fig2 = px.bar(latest, x='emp_rate', y='geo', orientation='h',
                  color='emp_rate', color_continuous_scale='Blues',
                  title=f'Employment Rate by Country ({latest_year})',
                  labels={'emp_rate':'Employment Rate','geo':'Country'})
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
    fig4 = px.scatter(filtered, x='employment_thousands', y='predicted',
                      color='sector', opacity=0.5,
                      labels={'employment_thousands':'Actual','predicted':'Predicted'},
                      hover_data=['geo','time'])
    mn = filtered['employment_thousands'].min()
    mx = filtered['employment_thousands'].max()
    fig4.add_shape(type='line', x0=mn, y0=mn, x1=mx, y1=mx,
                   line=dict(color='red', dash='dash'))
    st.plotly_chart(fig4, use_container_width=True)
 
