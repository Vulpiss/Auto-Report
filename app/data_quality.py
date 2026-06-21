from typing import Dict, Any
import pandas as pd


def analyze_raw_dataframe(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    category_col: str
) -> Dict[str, Any]:
    """
    Basic data quality diagnostics for the uploaded/source CSV.

    This function does not modify the data.
    It only reports potential issues.
    """

    total_rows = len(df)

    missing_date = int(df[date_col].isna().sum()) if date_col in df.columns else total_rows
    missing_value = int(df[value_col].isna().sum()) if value_col in df.columns else total_rows
    missing_category = int(df[category_col].isna().sum()) if category_col in df.columns else total_rows

    invalid_dates = 0
    if date_col in df.columns:
        parsed_dates = pd.to_datetime(df[date_col], errors="coerce")
        invalid_dates = int(parsed_dates.isna().sum() - missing_date)
        if invalid_dates < 0:
            invalid_dates = 0

    negative_values = 0
    if value_col in df.columns:
        numeric_values = pd.to_numeric(df[value_col], errors="coerce")
        negative_values = int((numeric_values < 0).sum())

    usable_rows = total_rows - max(
        missing_date,
        missing_value,
        missing_category,
        invalid_dates
    )

    if usable_rows < 0:
        usable_rows = 0

    dropped_rows_estimate = total_rows - usable_rows

    return {
        "total_rows": total_rows,
        "usable_rows_estimate": usable_rows,
        "dropped_rows_estimate": dropped_rows_estimate,
        "missing_date": missing_date,
        "missing_value": missing_value,
        "missing_category": missing_category,
        "invalid_dates": invalid_dates,
        "negative_values": negative_values,
    }


def build_quality_notes(quality: Dict[str, Any]) -> list[str]:
    notes = [
        f"Rows loaded: {quality.get('total_rows', 0)}",
        f"Estimated usable rows: {quality.get('usable_rows_estimate', 0)}",
        f"Estimated dropped rows: {quality.get('dropped_rows_estimate', 0)}",
        f"Missing date values: {quality.get('missing_date', 0)}",
        f"Missing numeric values: {quality.get('missing_value', 0)}",
        f"Missing category values: {quality.get('missing_category', 0)}",
        f"Invalid date values: {quality.get('invalid_dates', 0)}",
        f"Negative numeric values: {quality.get('negative_values', 0)}",
    ]

    return notes