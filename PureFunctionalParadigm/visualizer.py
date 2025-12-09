import os
import matplotlib.pyplot as plt
from utils import safe_float


# --- Pure Functional Style Helpers ---

def extract_column(rows, column):
    """Recursively extract a column from list of dicts."""
    if not rows:
        return []
    head, *tail = rows
    return [head.get(column)] + extract_column(tail, column)


def extract_numeric_column(rows, column):
    """Recursively extract numeric values."""
    if not rows:
        return []
    head, *tail = rows
    return [safe_float(head.get(column, 0))] + extract_numeric_column(tail, column)


def extract_two_numeric_columns(rows, col1, col2):
    """Build pairs (col1, col2) recursively."""
    if not rows:
        return []
    head, *tail = rows
    return [(safe_float(head.get(col1, 0)), safe_float(head.get(col2, 0)))] + \
           extract_two_numeric_columns(tail, col1, col2)


# --- Visualization Functions (IO side-effect, allowed) ---

def plot_line(dates, values, save_path):
    plt.figure(figsize=(10, 5))
    plt.plot(dates, values, marker="o")
    plt.xlabel("Date")
    plt.ylabel("Sales")
    plt.title("Sales Over Time")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_bar(labels, values, save_path):
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.xlabel("Region")
    plt.ylabel("Total Sales")
    plt.title("Sales by Region")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_hist(values, save_path):
    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=10)
    plt.xlabel("Sales")
    plt.ylabel("Frequency")
    plt.title("Sales Distribution")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def plot_scatter(x, y, save_path):
    plt.figure(figsize=(8, 5))
    plt.scatter(x, y)
    plt.xlabel("Sales")
    plt.ylabel("SalesGrowth")
    plt.title("Sales vs Growth")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
