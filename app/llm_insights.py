import json
from typing import Dict, Any

from app.llm_client import call_llm_with_retry


def build_insights_prompt(payload: Dict[str, Any]) -> str:
    payload_json = json.dumps(payload, ensure_ascii=False, indent=2)

    return f"""
SYSTEM:
You are a data analyst. Be factual and conservative.
Use ONLY the provided metrics. Do not invent data.
Return ONLY valid JSON.

USER:
INPUT:
{payload_json}

OUTPUT JSON:
{{
  "executive_summary": "string",
  "key_insights": ["string"],
  "risks_anomalies": ["string"],
  "recommended_actions": ["string"],
  "questions_to_ask": ["string"]
}}
""".strip()


def parse_and_validate(text: str) -> Dict[str, Any]:
    data = json.loads(text)

    required = [
        "executive_summary",
        "key_insights",
        "risks_anomalies",
        "recommended_actions",
        "questions_to_ask"
    ]

    for key in required:
        if key not in data:
            raise ValueError(f"Missing key: {key}")

    if not isinstance(data["executive_summary"], str):
        raise ValueError("executive_summary must be a string")

    for key in [
        "key_insights",
        "risks_anomalies",
        "recommended_actions",
        "questions_to_ask"
    ]:
        if not isinstance(data[key], list):
            raise ValueError(f"{key} must be a list")

    return data


def format_money(value: float) -> str:
    return f"{value:,.2f}"


def format_number(value: float) -> str:
    return f"{value:.2f}"


def fallback_insights(payload: Dict[str, Any]) -> Dict[str, Any]:
    kpis = payload.get("kpis", {})
    comparison = payload.get("comparison", {})

    total_value = float(kpis.get("total_value", 0.0))
    avg_value = float(kpis.get("avg_value", 0.0))
    rows_cnt = int(kpis.get("rows_cnt", 0))

    baseline_available = comparison.get("baseline_available", False)

    key_insights = [
        f"Total value: {format_money(total_value)}",
        f"Average value: {format_number(avg_value)}",
        f"Rows analyzed: {rows_cnt}",
    ]

    risks_anomalies = [
        "LLM insights unavailable.",
        "The report was generated using deterministic KPI calculations and fallback explanations.",
    ]

    recommended_actions = [
        "Review the KPI Summary and charts manually.",
        "Validate whether top categories are expected or indicate concentration risk.",
        "Rerun the report after enabling the LLM layer if qualitative commentary is required.",
        "Use this fallback report as a reliable numeric baseline.",
    ]

    questions_to_ask = [
        "Are the top categories expected for this dataset?",
        "Are there any missing or invalid values in the source CSV?",
        "Should the report include deeper data quality diagnostics?",
        "Should LLM insights be enabled for narrative analysis?",
    ]

    if baseline_available:
        change_pct = comparison.get("change_pct", {})
        total_change = float(change_pct.get("total_value", 0.0))
        avg_change = float(change_pct.get("avg_value", 0.0))

        key_insights.append(
            f"Total value change vs previous period: {format_number(total_change)}%"
        )
        key_insights.append(
            f"Average value change vs previous period: {format_number(avg_change)}%"
        )

        questions_to_ask.append(
            "What explains the change compared with the previous period?"
        )
    else:
        key_insights.append(
            "Previous period comparison is unavailable because no baseline data exists."
        )
        risks_anomalies.append(
            "Previous-period comparison is not reliable because the baseline period contains no data."
        )
        recommended_actions.append(
            "Add historical data before interpreting period-over-period growth."
        )
        questions_to_ask.append(
            "Does the dataset include enough historical records for period comparison?"
        )

    return {
        "executive_summary": (
            "LLM unavailable. Showing rule-based fallback summary based on calculated KPIs."
        ),
        "key_insights": key_insights,
        "risks_anomalies": risks_anomalies,
        "recommended_actions": recommended_actions,
        "questions_to_ask": questions_to_ask,
    }


def generate_insights(payload: Dict[str, Any]) -> Dict[str, Any]:
    try:
        prompt = build_insights_prompt(payload)
        raw = call_llm_with_retry(prompt)
        return parse_and_validate(raw)
    except Exception:
        return fallback_insights(payload)