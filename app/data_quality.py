from app.validation import CsvProfile, inspect_records


def analyze_raw_dataframe(df, date_col, value_col, category_col):
    _, quality = inspect_records(enumerate(df.to_dict("records"), 2), CsvProfile(date_col, value_col, category_col))
    return quality


def build_quality_notes(quality):
    return [
        f"Rekordy źródłowe: {quality['total_rows']}. Poprawne: {quality['valid_rows']}. Błędne: {quality['invalid_rows']}.",
        "Błędny rekord blokuje cały raport. Żadne rekordy nie są odrzucane po cichu.",
        f"Identyczne pełne wiersze CSV: {quality.get('exact_duplicate_rows', 0)}. Puste linie: {quality.get('blank_lines', 0)}. Wierszy z danymi nie usuwano.",
        f"Powtórzenia daty, kwoty i kategorii: {quality['duplicate_rows']}. Zachowano je; nie dowodzą błędu.",
        f"Kwoty ujemne: {quality['negative_values']}. Uwzględnione w sumie zgodnie z profilem.",
    ]
