# pipeline.py
import csv
import json
from collections import defaultdict
from utils import parse_date, safe_float, write_csv, stats_summary

# -------- Loading --------
def load_csv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(dict(r))
    return rows

def load_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    # expecting list of objects
    if isinstance(data, dict):
        # try to extract a list under common keys
        for key in ("data", "items", "rows"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return data

# -------- Cleaning --------
def handle_missing(rows, strategy="fill", fill_values=None, required_fields=None):
    """
    strategy: "fill" or "remove"
    fill_values: dict of {field: default}
    required_fields: list of fields that must be present (if remove and any missing -> remove)
    """
    out = []
    for r in rows:
        row = dict(r)  # mutable copy
        missing = False
        if required_fields:
            for f in required_fields:
                if row.get(f, "") == "" or row.get(f) is None:
                    missing = True
                    break
        if missing and strategy == "remove":
            continue
        # fill defaults
        if strategy == "fill" and fill_values:
            for k, v in fill_values.items():
                if row.get(k, "") == "" or row.get(k) is None:
                    row[k] = v
        out.append(row)
    return out

def standardize_dates(rows, date_fields):
    for r in rows:
        for f in date_fields:
            if f in r:
                r[f] = parse_date(r[f])
    return rows

def standardize_numbers(rows, numeric_fields, precision=2):
    for r in rows:
        for f in numeric_fields:
            if f in r:
                val = safe_float(r.get(f, 0))
                r[f] = round(val, precision)
    return rows

# -------- Transformation --------
def filter_rows(rows, condition_fn):
    """condition_fn takes a row and returns True to keep"""
    out = []
    for r in rows:
        if condition_fn(r):
            out.append(r)
    return out

def compute_sales_growth(rows, current_column="Sales", previous_column="PreviousSales", new_column="SalesGrowth"):
    for r in rows:
        cur = safe_float(r.get(current_column, 0))
        prev = safe_float(r.get(previous_column, 0))
        if prev != 0:
            r[new_column] = round((cur - prev) / prev, 4)
        else:
            r[new_column] = 0.0
    return rows

# -------- Aggregation --------
def aggregate_sum_by_key(rows, key_field, sum_field):
    agg = defaultdict(float)
    for r in rows:
        k = r.get(key_field, "UNKNOWN")
        val = safe_float(r.get(sum_field, 0))
        agg[k] += val
    # return list of dicts
    return [{"key": k, sum_field: round(v, 2)} for k, v in agg.items()]

# -------- Analysis --------
def numeric_column_list(rows, column):
    out = []
    for r in rows:
        try:
            v = float(r.get(column))
            out.append(v)
        except Exception:
            continue
    return out

def analyze_statistics(rows, numeric_columns):
    result = {}
    for col in numeric_columns:
        vals = numeric_column_list(rows, col)
        result[col] = stats_summary(vals)
    return result

# -------- Output Helpers --------
def save_clean_data(rows, output_path):
    if not rows:
        return
    fieldnames = list(rows[0].keys())
    write_csv(output_path, fieldnames, rows)

def save_analysis_summary(summary_dict, output_path):
    lines = []
    for col, s in summary_dict.items():
        lines.append(f"Column: {col}")
        for k, v in s.items():
            lines.append(f"  {k}: {v}")
        lines.append("")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
