from typing import List
import pandas as pd


class DataValidationError(Exception):
    pass


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: List[str],
) -> None:
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        raise DataValidationError(
            f"Missing required columns: {', '.join(missing)}"
        )


def validate_not_empty(df: pd.DataFrame) -> None:
    if df.empty:
        raise DataValidationError("Input CSV is empty.")


def validate_date_column(df: pd.DataFrame, date_col: str) -> None:
    parsed = pd.to_datetime(df[date_col], errors="coerce")

    if parsed.notna().sum() == 0:
        raise DataValidationError(
            f"Date column '{date_col}' contains no valid dates."
        )


def validate_value_column(df: pd.DataFrame, value_col: str) -> None:
    numeric = pd.to_numeric(df[value_col], errors="coerce")

    if numeric.notna().sum() == 0:
        raise DataValidationError(
            f"Value column '{value_col}' contains no valid numeric values."
        )


def validate_input_dataframe(
    df: pd.DataFrame,
    date_col: str,
    value_col: str,
    category_col: str,
) -> None:
    validate_not_empty(df)
    validate_required_columns(df, [date_col, value_col, category_col])
    validate_date_column(df, date_col)
    validate_value_column(df, value_col)