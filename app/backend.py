from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
import pandas as pd
import os

# Prometheus instrumentation
try:
    from prometheus_fastapi_instrumentator import Instrumentator
    INSTRUMENTATOR_AVAILABLE = True
except Exception:
    INSTRUMENTATOR_AVAILABLE = False

app = FastAPI(title='E-commerce Analytics API')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = Path('data')
CACHE_DIR = Path('cache')

# Allow overriding via env for production
DATA_DIR = Path(os.getenv('DATA_DIR', DATA_DIR))
CACHE_DIR = Path(os.getenv('CACHE_DIR', CACHE_DIR))


def read_json_cache(name: str):
    p = CACHE_DIR / f"{name}.json"
    if not p.exists():
        raise FileNotFoundError(p)
    return json.loads(p.read_text(encoding='utf8'))


@app.get('/kpis')
def get_kpis():
    try:
        return read_json_cache('kpis')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='KPIs not precomputed. Run scripts/precompute.py')


@app.get('/top_products')
def get_top_products():
    try:
        return read_json_cache('top_products')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Top products not precomputed. Run scripts/precompute.py')


@app.get('/monthly_trends')
def get_monthly_trends():
    try:
        return read_json_cache('monthly_trends')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Monthly trends not precomputed. Run scripts/precompute.py')


@app.get('/revenue_by_location')
def get_revenue_by_location():
    try:
        return read_json_cache('revenue_by_location')
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail='Revenue by location not precomputed. Run scripts/precompute.py')


@app.get('/orders')
def get_orders(limit: int = 1000):
    # stream a small sample of orders
    orders_csv = DATA_DIR / 'orders.csv'
    if not orders_csv.exists():
        raise HTTPException(status_code=404, detail='orders.csv not found in data dir')
    df = pd.read_csv(orders_csv, parse_dates=['order_date'])
    return df.head(limit).to_dict(orient='records')


if INSTRUMENTATOR_AVAILABLE:
    Instrumentator().instrument(app).expose(app)
