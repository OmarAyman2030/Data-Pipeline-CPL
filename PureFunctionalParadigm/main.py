import os
from pipeline import (
    load_csv, handle_missing, standardize_dates, standardize_numbers,
    filter_rows, compute_sales_growth, aggregate_sum_by_key,
    analyze_statistics
)
from utils import write_csv, safe_float

from visualizer import (
    extract_column, extract_numeric_column, extract_two_numeric_columns,
    plot_line, plot_bar, plot_hist, plot_scatter
)

PROJECT_ROOT = os.path.dirname(__file__)
DATA_DIR = os.path.join(PROJECT_ROOT, "..", "Data")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "..", "Output", "PureFunctionalParadigm")
VISUAL_DIR = os.path.join(OUTPUT_DIR, "Visuals")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(VISUAL_DIR, exist_ok=True)


def main():
    csv_path = os.path.join(DATA_DIR, "input.csv")
    rows = load_csv(csv_path)
    print(f"Loaded {len(rows)} rows")

    rows = handle_missing(
        rows,
        fill_values={
            "Date": "UNKNOWN",
            "Region": "UNKNOWN",
            "Sales": 0.0,
            "PreviousSales": 0.0,
            "Product": "UNKNOWN"
        }
    )

    rows = standardize_dates(rows, ["Date"])
    rows = standardize_numbers(rows, ["Sales", "PreviousSales"], precision=2)
    rows = filter_rows(rows, lambda r: safe_float(r.get("Sales", 0)) > 1000)
    rows = compute_sales_growth(rows, "Sales", "PreviousSales", "SalesGrowth")
    agg = aggregate_sum_by_key(rows, "Region", "Sales")
    stats = analyze_statistics(rows, ["Sales", "SalesGrowth"])

    # Save outputs
    clean_out = os.path.join(OUTPUT_DIR, "clean_data.csv")
    write_csv(clean_out, fieldnames=list(rows[0].keys()), rows=rows)
    print(f"Saved cleaned data to {clean_out}")

    agg_out = os.path.join(OUTPUT_DIR, "agg_by_region.csv")
    write_csv(agg_out, fieldnames=list(agg[0].keys()), rows=agg)
    print(f"Saved aggregation to {agg_out}")

    summary_out = os.path.join(OUTPUT_DIR, "analysis_summary.txt")
    with open(summary_out, "w", encoding="utf-8") as f:
        for col, s in stats.items():
            f.write(f"Column: {col}\n")
            for k, v in s.items():
                f.write(f"  {k}: {v}\n")
            f.write("\n")
    print(f"Saved analysis summary to {summary_out}")
    

    # 1. Line Chart: Sales Over Time
    dates = extract_column(rows, "Date")
    sales = extract_numeric_column(rows, "Sales")
    plot_line(dates, sales, os.path.join(VISUAL_DIR, "sales_over_time.png"))

    # 2. Bar Chart: Aggregated Sales by Region
    regions = extract_column(agg, "key")
    region_sales = extract_numeric_column(agg, "Sales")
    plot_bar(regions, region_sales, os.path.join(VISUAL_DIR, "sales_by_region.png"))

    # 3. Histogram: Sales distribution
    plot_hist(sales, os.path.join(VISUAL_DIR, "sales_histogram.png"))

    # 4. Scatter: Sales vs Growth
    pairs = extract_two_numeric_columns(rows, "Sales", "SalesGrowth")
    x_vals = [p[0] for p in pairs]
    y_vals = [p[1] for p in pairs]
    plot_scatter(x_vals, y_vals, os.path.join(VISUAL_DIR, "sales_vs_growth.png"))

    print(f"Visualizations saved to {VISUAL_DIR}")


if __name__ == "__main__":
    main()
