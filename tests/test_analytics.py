import pandas as pd
from src.analytics import compute_kpis, top_products, monthly_trends


def make_sample_orders():
    df = pd.DataFrame([
        {'order_id': 1, 'revenue': 100.0, 'profit': 30.0, 'discount_pct': 0.1, 'order_date': pd.Timestamp('2023-01-01'), 'quantity': 1, 'product_id': 1},
        {'order_id': 2, 'revenue': 200.0, 'profit': 50.0, 'discount_pct': 0.2, 'order_date': pd.Timestamp('2023-01-15'), 'quantity': 2, 'product_id': 2},
        {'order_id': 3, 'revenue': 150.0, 'profit': 40.0, 'discount_pct': 0.0, 'order_date': pd.Timestamp('2023-02-01'), 'quantity': 1, 'product_id': 1},
    ])
    return df


def test_compute_kpis():
    df = make_sample_orders()
    k = compute_kpis(df)
    assert k['total_revenue'] == 450.0
    assert k['total_profit'] == 120.0
    assert k['total_orders'] == 3


def test_top_products():
    df = make_sample_orders()
    products = pd.DataFrame([{'product_id':1,'product_name':'A'},{'product_id':2,'product_name':'B'}])
    top = top_products(df, products, top_n=2)
    assert top.iloc[0]['product_id'] in [1,2]


def test_monthly_trends():
    df = make_sample_orders()
    mt = monthly_trends(df)
    assert 'revenue' in mt.columns
