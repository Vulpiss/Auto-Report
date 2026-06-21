import os
import random
from datetime import date, timedelta

import pandas as pd


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_sample_with_baseline(
    output_path: str,
    start_date: str = "2023-09-01",
    days: int = 240,
) -> None:
    random.seed(42)

    categories = ["Electronics", "Home", "Clothing", "Sports", "Food"]
    start = date.fromisoformat(start_date)

    rows = []

    for i in range(days):
        current_date = start + timedelta(days=i)

        for _ in range(random.randint(3, 8)):
            category = random.choices(
                categories,
                weights=[0.45, 0.18, 0.15, 0.12, 0.10],
                k=1,
            )[0]

            base_value = {
                "Electronics": 700,
                "Home": 250,
                "Clothing": 180,
                "Sports": 160,
                "Food": 120,
            }[category]

            trend_multiplier = 1.0 if i < days // 2 else 1.18

            value = round(
                random.uniform(base_value * 0.6, base_value * 1.4) * trend_multiplier,
                2,
            )

            rows.append(
                {
                    "date": current_date.isoformat(),
                    "value": value,
                    "category": category,
                }
            )

    df = pd.DataFrame(rows)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)

    print(f"Saved: {output_path}")
    print(f"Rows: {len(df)}")
    print(f"Date range: {df['date'].min()} -> {df['date'].max()}")


if __name__ == "__main__":
    output_file = os.path.join(BASE_DIR, "sample_data", "input_with_baseline.csv")
    generate_sample_with_baseline(output_file)