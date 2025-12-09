import os
import matplotlib.pyplot as plt
from utils import safe_float


# -------------------------
#  Imperative Helper Tools
# -------------------------

def extract_column(rows, column):
   
    out = []
    for r in rows:
        out.append(r.get(column))
    return out


def extract_numeric_column(rows, column):
    out = []
    for r in rows:
        out.append(safe_float(r.get(column, 0)))
    return out


def extract_two_numeric_columns(rows, col1, col2):
    xs = []
    ys = []
    for r in rows:
        xs.append(safe_float(r.get(col1, 0)))
        ys.append(safe_float(r.get(col2, 0)))
    return xs, ys




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
