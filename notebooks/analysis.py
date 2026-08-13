"""Run example analysis: compute KPIs and produce simple plots."""
import sys
from pathlib import Path

# Ensure project root is on sys.path so `from src...` works when running this
# script directly (sys.path[0] is the notebooks/ folder when executed as a script).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import argparse
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from src.analytics import load_data, compute_kpis, top_products, revenue_by_location, monthly_trends

sns.set(style='whitegrid')


def main(data_dir, out_dir):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    ds = load_data(data_dir)
    orders = ds['orders']

    kpis = compute_kpis(orders)
    print('KPIs:')
    for k, v in kpis.items():
        print(f" - {k}: {v}")

    # Save KPIs
    pd.Series(kpis).to_csv(out / 'kpis.csv')

    # Top products
    top = top_products(orders, ds['products'], top_n=10)
    top.to_csv(out / 'top_products.csv', index=False)

    # Revenue by location
    rloc = revenue_by_location(orders, ds['locations'])
    rloc.to_csv(out / 'revenue_by_location.csv', index=False)

    # Monthly trends
    months = monthly_trends(orders)
    months.to_csv(out / 'monthly_trends.csv', index=False)

    # Plots
    plt.figure(figsize=(10,6))
    sns.lineplot(data=months, x='month', y='revenue')
    plt.title('Monthly Revenue')
    plt.tight_layout()
    plt.savefig(out / 'monthly_revenue.png')
    plt.close()

    plt.figure(figsize=(10,6))
    sns.barplot(data=top, x='revenue', y='product_name')
    plt.title('Top 10 Products by Revenue')
    plt.tight_layout()
    plt.savefig(out / 'top_products.png')
    plt.close()

    plt.figure(figsize=(10,6))
    sns.barplot(data=rloc.head(10), x='revenue', y='location_name')
    plt.title('Top Locations by Revenue')
    plt.tight_layout()
    plt.savefig(out / 'top_locations.png')
    plt.close()

    print('Saved KPI CSVs and plots to', out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--data', default='data')
    parser.add_argument('--out', default='output')
    args = parser.parse_args()
    main(args.data, args.out)
