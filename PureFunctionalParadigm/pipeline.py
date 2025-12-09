import csv
import json
import sys
from utils import parse_date, safe_float, stats_summary

# زيادة حد العودية لأننا سنعتمد عليها كلياً بدلاً من الحلقات
sys.setrecursionlimit(5000)


# -------- Loading --------
# (IO operations remain Impure by definition, but we keep them isolated)
def load_csv(path):
    with open(path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [dict(r) for r in reader]


def load_json(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        for key in ("data", "items", "rows"):
            if key in data and isinstance(data[key], list):
                return data[key]
        return [data]
    return data


# ==========================================
#  CORE RECURSIVE PATTERNS (The Engine)
# ==========================================
# [Concept: Higher-Order Functions]
# [Concept: Tail Recursion & Accumulators]
# [Concept: Pattern Matching Simulation (Head | Tail)]

def recursive_map(func, lst, acc=None):
    """
    تطبيق دالة على قائمة باستخدام العودية الذيلية والمراكم.
    تطابق مفهوم: Map F L -> L'
    """
    if acc is None:
        acc = []

    # Base Case: Empty List -> Return Accumulator
    if not lst:
        return acc

    # Recursive Step: Process Head, Add to Acc, Recurse on Tail
    head, *tail = lst
    processed_val = func(head)
    # [Concept: Invariant Programming] - Adding to Accumulator
    return recursive_map(func, tail, acc + [processed_val])


def recursive_filter(condition_fn, lst, acc=None):
    """
    تصفية قائمة باستخدام العودية الذيلية.
    """
    if acc is None:
        acc = []

    if not lst:
        return acc

    head, *tail = lst
    if condition_fn(head):
        new_acc = acc + [head]
    else:
        new_acc = acc

    return recursive_filter(condition_fn, tail, new_acc)


# -------- Cleaning --------

def handle_missing(rows, fill_values=None):
    # [Concept: Contextual Environment / Closure]
    # المتغير fill_values موجود في البيئة الخارجية ويتم استدعاؤه داخل fill_row
    fill_values = fill_values or {}

    def fill_row(r):
        # [Concept: Functional / Stateless] - Creating new dict
        return {k: (v if v not in [None, ""] else fill_values.get(k, v)) for k, v in r.items()}

    # [Concept: Recursion instead of Loop]
    return recursive_map(fill_row, rows)


def standardize_dates(rows, date_fields):
    # [Concept: Closure]
    def standardize_row(r):
        return {**r, **{f: parse_date(r.get(f)) for f in date_fields if f in r}}

    return recursive_map(standardize_row, rows)


def standardize_numbers(rows, numeric_fields, precision=2):
    # [Concept: Closure]
    def standardize_row(r):
        return {k: round(safe_float(v), precision) if k in numeric_fields else v
                for k, v in r.items()}

    return recursive_map(standardize_row, rows)


# -------- Transformation --------

def filter_rows(rows, condition_fn):
    # [Concept: Higher-Order Function] - condition_fn passed as argument
    # [Concept: Tail Recursion] - using recursive_filter
    return recursive_filter(condition_fn, rows)


def compute_sales_growth(rows, current_column="Sales", previous_column="PreviousSales", new_column="SalesGrowth"):
    # [Concept: Closure] capturing column names
    def compute_row(r):
        cur = safe_float(r.get(current_column, 0))
        prev = safe_float(r.get(previous_column, 0))
        new_val = round((cur - prev) / prev, 4) if prev != 0 else 0.0
        return {**r, new_column: new_val}

    return recursive_map(compute_row, rows)


# -------- Aggregation --------

def aggregate_sum_by_key(rows, key_field, sum_field):
    """
    تنفيذ التجميع باستخدام العودية الذيلية والمراكم (Dictionary Accumulator).
    هذا يطبق مبدأ Invariant Programming بوضوح:
    كل خطوة تنقل قيمة من القائمة (S) إلى المراكم (A).
    """

    # Helper recursive function (Invariant Loop)
    def aggregate_recursive(lst, accumulator):
        # Base Case
        if not lst:
            return accumulator

        # Recursive Step
        head, *tail = lst
        key = head.get(key_field, "UNKNOWN")
        val = safe_float(head.get(sum_field, 0))

        # Update Accumulator (Creating new state ideally, but updating dict for pragmatic reasons)
        current_sum = accumulator.get(key, 0.0)
        # Note: To be purely functional, we should create a new dict, but Python dict copy is expensive.
        # We will act as if we are creating a new state passed to the next recursion.
        new_acc = accumulator.copy()
        new_acc[key] = current_sum + val

        return aggregate_recursive(tail, new_acc)

    # 1. Calculate Sums Recursively
    raw_sums = aggregate_recursive(rows, {})

    # 2. Format Output (Transformation)
    # تحويل القاموس الناتج إلى قائمة قواميس
    def format_output(item):
        k, v = item
        return {"key": k, sum_field: round(v, 2)}

    # بما أن map تعمل على القوائم، نحول الـ items لقائمة
    return recursive_map(format_output, list(raw_sums.items()))


# -------- Analysis --------

def numeric_column_list(rows, column):
    # دالة مساعدة لاستخراج القيمة
    def get_val(r):
        return safe_float(r.get(column))

    # دالة شرطية
    def is_valid(r):
        return r.get(column) not in [None, ""]

    # 1. Filter valid rows (Recursive)
    valid_rows = recursive_filter(is_valid, rows)
    # 2. Map to numbers (Recursive)
    return recursive_map(get_val, valid_rows)


def analyze_statistics(rows, numeric_columns):
    # [Concept: Higher-Order Function & Recursion]
    # بدلاً من حلقة for على الأعمدة، نستخدم العودية لبناء قاموس النتائج

    def analyze_cols_recursive(cols, acc):
        if not cols:
            return acc

        head_col, *tail_cols = cols
        vals = numeric_column_list(rows, head_col)

        new_acc = acc.copy()
        new_acc[head_col] = stats_summary(vals)

        return analyze_cols_recursive(tail_cols, new_acc)

    return analyze_cols_recursive(numeric_columns, {})