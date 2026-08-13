"""Analytics helpers for e-commerce KPIs."""
from pathlib import Path
import pandas as pd


def load_data(data_dir):
    d = Path(data_dir)
    orders = pd.read_csv(d / 'orders.csv', parse_dates=['order_date'])
    customers = pd.read_csv(d / 'customers.csv', parse_dates=['join_date'])
    products = pd.read_csv(d / 'products.csv')
    categories = pd.read_csv(d / 'categories.csv')
    locations = pd.read_csv(d / 'locations.csv')
    return {'orders': orders, 'customers': customers, 'products': products, 'categories': categories, 'locations': locations}


def compute_kpis(orders_df):
    total_revenue = orders_df['revenue'].sum()
    total_profit = orders_df['profit'].sum()
    total_orders = orders_df['order_id'].nunique()
    avg_order_value = total_revenue / total_orders if total_orders else 0
    avg_discount = orders_df['discount_pct'].mean()
    return {
        'total_revenue': float(total_revenue),
        'total_profit': float(total_profit),
        'total_orders': int(total_orders),
        'avg_order_value': float(avg_order_value),
        'avg_discount_pct': float(avg_discount)
    }


def top_products(orders_df, products_df, top_n=10):
    grouped = orders_df.groupby('product_id').agg({'revenue': 'sum', 'quantity': 'sum'}).reset_index()
    merged = grouped.merge(products_df[['product_id', 'product_name']], on='product_id', how='left')
    return merged.sort_values('revenue', ascending=False).head(top_n)


def revenue_by_location(orders_df, locations_df):
    grp = orders_df.groupby('location_id').agg({'revenue': 'sum', 'profit': 'sum', 'order_id': 'nunique'}).reset_index()
    return grp.merge(locations_df, on='location_id', how='left').sort_values('revenue', ascending=False)


def monthly_trends(orders_df):
    df = orders_df.copy()
    # Ensure `order_date` is datetime-like (backend JSON may provide strings)
    if not pd.api.types.is_datetime64_any_dtype(df.get('order_date')):
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')
    df['month'] = df['order_date'].dt.to_period('M').dt.to_timestamp()
    grp = df.groupby('month').agg({'revenue': 'sum', 'profit': 'sum', 'order_id': 'nunique'}).reset_index()
    grp = grp.rename(columns={'order_id': 'num_orders'})
    return grp


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data')
    parser.add_argument('--out', default='output')
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    ds = load_data(args.data)
    kpis = compute_kpis(ds['orders'])
    pd.Series(kpis).to_csv(out / 'kpis.csv')
    top = top_products(ds['orders'], ds['products'])
    top.to_csv(out / 'top_products.csv', index=False)
    revenue_by_location(ds['orders'], ds['locations']).to_csv(out / 'revenue_by_location.csv', index=False)
    monthly_trends(ds['orders']).to_csv(out / 'monthly_trends.csv', index=False)
    print('Analysis outputs written to', out)
