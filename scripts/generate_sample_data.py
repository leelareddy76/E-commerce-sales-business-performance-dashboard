"""Generate synthetic e-commerce dataset CSVs.

Produces: Orders.csv, Customers.csv, Products.csv, Categories.csv, Locations.csv
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

RNG = np.random.default_rng(42)


def random_dates(start, end, n):
    start_u = start.value // 10**9
    end_u = end.value // 10**9
    return pd.to_datetime(RNG.integers(start_u, end_u, size=n), unit='s')


def make_categories(n_categories=8):
    cat_ids = np.arange(1, n_categories+1)
    cats = [f"Category {i}" for i in cat_ids]
    return pd.DataFrame({'category_id': cat_ids, 'category_name': cats})


def make_locations(n_locations=6):
    locs = [f"City {i}" for i in range(1, n_locations+1)]
    return pd.DataFrame({'location_id': np.arange(1, n_locations+1), 'location_name': locs})


def make_products(n_products=80, categories=None):
    if categories is None:
        categories = make_categories()
    cat_ids = categories['category_id'].to_numpy()
    product_ids = np.arange(1, n_products+1)
    product_names = [f"Product {i}" for i in product_ids]
    category_choices = RNG.choice(cat_ids, size=n_products)
    prices = np.round(RNG.uniform(5, 500, size=n_products), 2)
    costs = np.round(prices * RNG.uniform(0.4, 0.8, size=n_products), 2)
    df = pd.DataFrame({'product_id': product_ids, 'product_name': product_names, 'category_id': category_choices, 'price': prices, 'cost': costs})
    df = df.merge(categories, on='category_id', how='left')
    return df


def make_customers(n_customers=300, locations=None, start_date=pd.Timestamp('2018-01-01'), end_date=pd.Timestamp('2023-12-31')):
    if locations is None:
        locations = make_locations()
    customer_ids = np.arange(1, n_customers+1)
    names = [f"Customer {i}" for i in customer_ids]
    location_choices = RNG.choice(locations['location_id'].to_numpy(), size=n_customers)
    join_dates = random_dates(pd.to_datetime(start_date), pd.to_datetime(end_date), n_customers)
    return pd.DataFrame({'customer_id': customer_ids, 'customer_name': names, 'location_id': location_choices, 'join_date': join_dates})


def make_orders(n_orders=2000, customers=None, products=None, locations=None, start_date=pd.Timestamp('2020-01-01'), end_date=pd.Timestamp('2023-12-31')):
    if customers is None:
        customers = make_customers(locations=locations)
    if products is None:
        products = make_products()
    if locations is None:
        locations = make_locations()

    order_ids = np.arange(1, n_orders+1)
    customer_choices = RNG.choice(customers['customer_id'].to_numpy(), size=n_orders)
    product_choices = RNG.choice(products['product_id'].to_numpy(), size=n_orders)
    quantities = RNG.integers(1, 6, size=n_orders)
    discount_pct = np.round(RNG.uniform(0.0, 0.4, size=n_orders), 2)  # up to 40%
    order_dates = random_dates(pd.to_datetime(start_date), pd.to_datetime(end_date), n_orders)
    location_choices = RNG.choice(locations['location_id'].to_numpy(), size=n_orders)

    prod_map = products.set_index('product_id')
    prices = prod_map.loc[product_choices, 'price'].to_numpy()
    costs = prod_map.loc[product_choices, 'cost'].to_numpy()

    revenue = np.round(prices * quantities * (1 - discount_pct), 2)
    total_cost = np.round(costs * quantities, 2)
    profit = np.round(revenue - total_cost, 2)

    df = pd.DataFrame({'order_id': order_ids, 'customer_id': customer_choices, 'product_id': product_choices, 'quantity': quantities, 'discount_pct': discount_pct, 'order_date': order_dates, 'location_id': location_choices, 'revenue': revenue, 'cost': total_cost, 'profit': profit})
    return df


def main(out_dir, n_orders=2000):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    categories = make_categories()
    locations = make_locations()
    products = make_products(categories=categories)
    customers = make_customers(locations=locations)
    orders = make_orders(n_orders=n_orders, customers=customers, products=products, locations=locations)

    categories.to_csv(out / 'categories.csv', index=False)
    locations.to_csv(out / 'locations.csv', index=False)
    products.to_csv(out / 'products.csv', index=False)
    customers.to_csv(out / 'customers.csv', index=False)
    orders.to_csv(out / 'orders.csv', index=False)

    print(f"Wrote CSVs to {out.resolve()}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='data', help='output directory')
    parser.add_argument('--n_orders', type=int, default=2000)
    args = parser.parse_args()
    main(args.out, n_orders=args.n_orders)
