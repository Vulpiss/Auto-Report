"""Local, deterministic explanations. No network calls or retry delays."""


def fallback_insights(payload):
    kpis = payload["kpis"]
    return {
        "executive_summary": "Wyniki dotyczą pozycji z wybranego okresu. Liczba pozycji nie jest liczbą zamówień.",
        "key_insights": [f"Liczba pozycji: {kpis['rows_cnt']}."],
        "risks_anomalies": [payload["comparison"]["reason"]],
        "recommended_actions": ["Porównaj sumę z eksportem źródłowym przy tych samych filtrach i definicji kwoty."],
        "questions_to_ask": [],
    }


def generate_insights(payload):
    return fallback_insights(payload)
