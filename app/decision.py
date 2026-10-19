def simple_decision(comparison):
    if not comparison.get("baseline_available"):
        return comparison.get("reason", "Brak wiarygodnego porównania.")
    change = comparison["change_pct"]["total_value"]
    if change is None:
        return "Zmiana procentowa sumy: N/A. Baza jest zerowa lub ujemna."
    formatted = f"{change:+.1f}".replace(".", ",")
    return f"Zmiana sumy: {formatted}%. To opis danych, nie zalecenie zwiększania sprzedaży ani wydatków."
