"""Precompute Parquet and cached JSON responses for fast dashboard API.

Writes to `cache/`:
- kpis.json
- top_products.json
- monthly_trends.json
- revenue_by_location.json

Also writes parquet files under `data_parquet/` for faster IO if desired.
"""
import sys
from pathlib import Path
import pandas as pd
import json

# Ensure project root is on sys.path so `from src.analytics` works when running this
# script directly (sys.path[0] would otherwise be the scripts/ folder).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analytics import compute_kpis, top_products, revenue_by_location, monthly_trends

DATA_DIR = Path('data')
CACHE_DIR = Path('cache')
PARQUET_DIR = Path('data_parquet')

CACHE_DIR.mkdir(exist_ok=True)
PARQUET_DIR.mkdir(exist_ok=True)


def to_json_serializable(obj):
    if hasattr(obj, 'to_dict'):
        return obj.to_dict(orient='records')
    return obj


def main():
    orders = pd.read_csv(DATA_DIR / 'orders.csv', parse_dates=['order_date'])
    products = pd.read_csv(DATA_DIR / 'products.csv')
    locations = pd.read_csv(DATA_DIR / 'locations.csv')

    # write parquet copies for faster IO
    orders.to_parquet(PARQUET_DIR / 'orders.parquet', index=False)
    products.to_parquet(PARQUET_DIR / 'products.parquet', index=False)
    locations.to_parquet(PARQUET_DIR / 'locations.parquet', index=False)

    # compute and cache kpis
    kpis = compute_kpis(orders)
    (CACHE_DIR / 'kpis.json').write_text(json.dumps(kpis), encoding='utf8')

    top = top_products(orders, products, top_n=50)
    (CACHE_DIR / 'top_products.json').write_text(json.dumps(top.to_dict(orient='records')), encoding='utf8')

    months = monthly_trends(orders)
    (CACHE_DIR / 'monthly_trends.json').write_text(json.dumps(months.to_dict(orient='records'), default=str), encoding='utf8')

    rloc = revenue_by_location(orders, locations)
    (CACHE_DIR / 'revenue_by_location.json').write_text(json.dumps(rloc.to_dict(orient='records')), encoding='utf8')

    print('Precompute complete. Cache written to', CACHE_DIR.resolve())


if __name__ == '__main__':
    main()
