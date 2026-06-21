from typing import Dict, Any


def simple_decision(comparison: Dict[str, Any]) -> str:
    """
    Rule-based decision layer.

    It avoids recommending SCALE when previous-period data is missing.
    """

    previous = comparison.get("previous", {})
    previous_rows = previous.get("rows_cnt", 0)

    change = comparison["change_pct"]["total_value"]

    if previous_rows == 0:
        return "NO BASELINE – INSUFFICIENT HISTORICAL DATA"

    if change < -10:
        return "NEGATIVE TREND – INVESTIGATE"

    if change > 20:
        return "STRONG GROWTH – SCALE"

    return "STABLE"