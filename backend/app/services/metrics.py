from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable


def safe_ratio(numerator: float, denominator: float, multiplier: float = 1.0) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * multiplier, 4)


def enrich_metrics(raw: dict[str, Any]) -> dict[str, Any]:
    cost = float(raw.get("cost") or 0)
    impressions = int(raw.get("impressions") or 0)
    clicks = int(raw.get("clicks") or 0)
    conversions = int(raw.get("conversions") or 0)
    return {
        **raw,
        "cost": round(cost, 2),
        "impressions": impressions,
        "clicks": clicks,
        "conversions": conversions,
        "ctr": safe_ratio(clicks, impressions, 100),
        "cvr": safe_ratio(conversions, clicks, 100),
        "cpa": safe_ratio(cost, conversions),
    }


def metric_delta(current: float | None, previous: float | None, inverse_good: bool = False) -> dict[str, Any]:
    current_value = float(current or 0)
    previous_value = float(previous or 0)
    absolute = round(current_value - previous_value, 2)
    percent = None if previous_value == 0 else round((absolute / previous_value) * 100, 1)
    improving = absolute < 0 if inverse_good else absolute > 0
    if absolute == 0:
        improving = None
    return {"absolute": absolute, "percent": percent, "improving": improving}


def latest_by_plan(rows: Iterable[dict[str, Any]]) -> dict[int, dict[str, Any]]:
    result: dict[int, dict[str, Any]] = {}
    for row in rows:
        plan_id = int(row["plan_id"])
        current = result.get(plan_id)
        if current is None or str(row["timestamp"]) > str(current["timestamp"]):
            result[plan_id] = row
    return result


def parse_timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))

