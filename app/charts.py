from datetime import date, timedelta
from pathlib import Path
from decimal import Decimal
import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
from matplotlib.ticker import FuncFormatter, MaxNLocator


def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)


def trend_figure(data, currency="PLN"):
    dates = [date.fromisoformat(d["event_date"]) for d in data]
    values = [float(d["total_value"]) for d in data]
    fig = Figure(figsize=(9, 3.2), layout="constrained")
    ax = fig.subplots()
    ax.bar(dates, values, color="#246a73", width=0.8)
    # Never show fictitious intraday times for daily data, including a single day.
    ticks = []
    if dates:
        first, last = min(dates), max(dates)
        span = (last - first).days
        step = max(1, (span + 4) // 5)
        ticks = [first + timedelta(days=n) for n in range(0, span + 1, step)]
        if ticks[-1] != last:
            # Replace the nearby final tick instead of adding overlapping labels.
            if len(ticks) > 1:
                ticks[-1] = last
            else:
                ticks.append(last)
    ax.set_xticks(ticks)
    ax.xaxis.set_major_formatter(DateFormatter("%d.%m.%Y"))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=5, steps=[1, 2, 5, 10], min_n_ticks=2))
    def tick_label(value, _):
        locations = ax.yaxis.get_majorticklocs()
        step = min((abs(b-a) for a, b in zip(locations, locations[1:]) if b != a), default=1)
        # Locator steps are 1/2/5 times a power of ten. Preserve their precision,
        # including fractional-cent axis ticks, rather than repeating "0".
        precision = max(0, -Decimal(f"{step:.8g}").normalize().as_tuple().exponent)
        if abs(value) < step * 1e-8:
            value = 0
        return f"{value:,.{precision}f}".replace(",", " ").replace(".", ",")
    ax.yaxis.set_major_formatter(FuncFormatter(tick_label))
    ax.set_ylabel(f"Wartość pozycji [{currency}]")
    ax.set_xlabel("Data")
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    return fig


def plot_trend(data, path, currency="PLN"):
    fig = trend_figure(data, currency)
    fig.savefig(path, dpi=160)
    return path


def plot_top_categories(data, path, currency="PLN"):
    fig = Figure(figsize=(8, 4), layout="constrained")
    ax = fig.subplots()
    labels = [d["category"][:45] for d in data][::-1]
    ax.barh(labels, [d["total_value"] for d in data][::-1], color="#246a73")
    ax.set_xlabel(f"Wartość pozycji [{currency}]")
    fig.savefig(path, dpi=160)
    return path
