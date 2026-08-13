import streamlit as st
from pathlib import Path
import pandas as pd
import plotly.express as px
import requests
from src.analytics import load_data, compute_kpis, top_products, revenue_by_location, monthly_trends

st.set_page_config(page_title='E‑commerce Analytics', layout='wide')

BACKEND_URL = st.sidebar.text_input('Backend URL (leave blank to load local files)', 'http://localhost:8000')
data_dir = st.sidebar.text_input('Local data directory (fallback)', 'data')
top_n = st.sidebar.slider('Top products', 5, 20, 10)

use_backend = bool(BACKEND_URL and BACKEND_URL.strip())

@st.cache_data
def load_ds_local(data_dir: str):
    return load_data(data_dir)

@st.cache_data
def fetch_from_backend(endpoint: str):
    resp = requests.get(f"{BACKEND_URL.rstrip('/')}/{endpoint}")
    resp.raise_for_status()
    return resp.json()

st.title('E‑commerce Sales & Business Performance')

if st.sidebar.button('Reload data'):
    load_ds_local.clear()
    fetch_from_backend.clear()

try:
    if use_backend:
        kpis = fetch_from_backend('kpis')
        orders = pd.DataFrame(fetch_from_backend('orders'))
        products = pd.DataFrame(fetch_from_backend('top_products'))
        locations = pd.DataFrame(fetch_from_backend('revenue_by_location'))
    else:
        ds = load_ds_local(data_dir)
        orders = ds['orders']
        products = ds['products']
        locations = ds['locations']
        kpis = compute_kpis(orders)
except Exception as e:
    st.error(f'Failed to load data: {e}')
    st.stop()

# KPIs
if not use_backend:
    kpis = compute_kpis(orders)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric('Total Revenue', f"${kpis['total_revenue']:,.2f}")
col2.metric('Total Profit', f"${kpis['total_profit']:,.2f}")
col3.metric('Total Orders', f"{kpis['total_orders']}")
col4.metric('Avg Order Value', f"${kpis['avg_order_value']:,.2f}")
col5.metric('Avg Discount', f"{kpis['avg_discount_pct']*100:.2f}%")

st.markdown('---')

# Monthly trend
st.header('Monthly Revenue')
if use_backend:
    months = pd.DataFrame(fetch_from_backend('monthly_trends'))
else:
    months = monthly_trends(orders)
fig = px.line(months, x='month', y='revenue', markers=True, title='Monthly Revenue')
st.plotly_chart(fig, width='stretch')

# Top products
st.header('Top Products by Revenue')
if use_backend:
    top = products.head(top_n)
else:
    top = top_products(orders, products, top_n=top_n)
fig2 = px.bar(top, x='revenue', y='product_name', orientation='h', title=f'Top {top_n} Products by Revenue')
st.plotly_chart(fig2, width='stretch')

# Revenue by location
st.header('Revenue by Location')
if use_backend:
    rloc = locations
else:
    rloc = revenue_by_location(orders, locations)
fig3 = px.bar(rloc, x='revenue', y='location_name', orientation='h', title='Revenue by Location')
st.plotly_chart(fig3, width='stretch')

# Data download
st.markdown('---')
st.header('Export')
colA, colB = st.columns(2)
with colA:
    st.download_button('Download KPIs CSV', pd.Series(kpis).to_csv(index=True), file_name='kpis.csv')
with colB:
    st.download_button('Download Top Products CSV', top.to_csv(index=False), file_name='top_products.csv')

st.info('Run `streamlit run app/streamlit_app.py` from the project root (with the .venv activated)')
