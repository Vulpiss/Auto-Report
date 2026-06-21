import os

import matplotlib

# Use non-GUI backend for PDF/report generation.
# This prevents warnings/errors when charts are generated from a desktop app thread.
matplotlib.use("Agg")

import matplotlib.pyplot as plt


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def plot_trend(data, path: str) -> str:
    """
    Generates daily trend chart and saves it as PNG.
    """

    dates = [d["event_date"] for d in data]
    values = [d["total_value"] for d in data]

    plt.figure(figsize=(10, 4))
    plt.plot(dates, values)

    if len(dates) > 10:
        step = max(1, len(dates) // 10)
        tick_positions = list(range(0, len(dates), step))
        tick_labels = [dates[i] for i in tick_positions]
        plt.xticks(tick_positions, tick_labels, rotation=45, ha="right")
    else:
        plt.xticks(rotation=45, ha="right")

    plt.title("Daily Trend")
    plt.xlabel("Date")
    plt.ylabel("Total value")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

    return path


def plot_top_categories(data, path: str) -> str:
    """
    Generates top categories horizontal bar chart and saves it as PNG.
    """

    categories = [d["category"] for d in data][::-1]
    values = [d["total_value"] for d in data][::-1]

    plt.figure(figsize=(8, 5))
    plt.barh(categories, values)

    plt.title("Top Categories")
    plt.xlabel("Total value")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()

    return path