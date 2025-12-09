# main.py
import os
from pipeline import (
    load_csv, load_json, handle_missing, standardize_dates, standardize_numbers,
    filter_rows, compute_sales_growth, aggregate_sum_by_key,
    analyze_statistics, save_clean_data, save_analysis_summary
)

from visualizer import (
    extract_column, extract_numeric_column, extract_two_numeric_columns,
    plot_line, plot_bar, plot_hist, plot_scatter
)

from utils import write_csv, safe_float

PROJECT_ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(PROJECT_ROOT, "..", "Data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "..", "Output", "ImperativeParadigm")
VISUAL_DIR = os.path.join(OUTPUT_DIR, "Visuals")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VISUAL_DIR, exist_ok=True)

def main():
    # 1. Load data (CSV example)
    csv_path = os.path.join(DATA_DIR, "input.csv")
    rows = load_csv(csv_path)
    print(f"Loaded {len(rows)} rows")

    # 2. Handle missing: remove rows missing Sales or Region (example)
    rows = handle_missing(
        rows,
        strategy="fill",
        fill_values={
            "Date": "UNKNOWN",
            "Region": "UNKNOWN",
            "Sales": 0.0,
            "PreviousSales": 0.0,
            "Product": "UNKNOWN",
            "SalesGrowth": 0.0
        }
    )

    # 3. Standardize dates and numbers
    rows = standardize_dates(rows, date_fields=["Date"])
    rows = standardize_numbers(rows, numeric_fields=["Sales", "PreviousSales"], precision=2)

    # 4. Filter rows (imperative): keep Sales > 1000
    rows = filter_rows(rows, lambda r: float(r.get("Sales", 0)) > 1000)

    # 5. Compute new column SalesGrowth
    rows = compute_sales_growth(rows, current_column="Sales", previous_column="PreviousSales", new_column="SalesGrowth")

    # 6. Aggregate: total sales by Region
    agg = aggregate_sum_by_key(rows, key_field="Region", sum_field="Sales")

    # 7. Analyze statistics
    stats = analyze_statistics(rows, numeric_columns=["Sales", "SalesGrowth"])

    # 8. Save results
    clean_out = os.path.join(OUTPUT_DIR, "clean_data.csv")
    save_clean_data(rows, clean_out)
    print(f"Saved cleaned data to {clean_out}")

    agg_out = os.path.join(OUTPUT_DIR, "agg_by_region.csv")
    # convert agg to CSV via pipeline utils
    if agg:
        from utils import write_csv
        write_csv(agg_out, fieldnames=list(agg[0].keys()), rows=agg)
        print(f"Saved aggregation to {agg_out}")

    summary_out = os.path.join(OUTPUT_DIR, "analysis_summary.txt")
    save_analysis_summary(stats, summary_out)
    print(f"Saved analysis summary to {summary_out}")
    

    # Line chart: Sales over time
    dates = extract_column(rows, "Date")
    sales = extract_numeric_column(rows, "Sales")
    plot_line(dates, sales, os.path.join(VISUAL_DIR, "sales_over_time.png"))

    # Bar chart: Sales by region
    regions = extract_column(agg, "key")
    region_sales = extract_numeric_column(agg, "Sales")
    plot_bar(regions, region_sales, os.path.join(VISUAL_DIR, "sales_by_region.png"))

    # Histogram: Sales distribution
    plot_hist(sales, os.path.join(VISUAL_DIR, "sales_histogram.png"))

    # Scatter: Sales vs Growth
    xs, ys = extract_two_numeric_columns(rows, "Sales", "SalesGrowth")
    plot_scatter(xs, ys, os.path.join(VISUAL_DIR, "sales_vs_growth.png"))

    print(f"Visualizations saved in: {VISUAL_DIR}")

if __name__ == "__main__":
    main()
