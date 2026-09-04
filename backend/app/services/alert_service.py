from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from ..database import connection


def _rule_map() -> dict[str, dict[str, Any]]:
    with connection() as conn:
        rows = conn.execute("SELECT * FROM alert_rules WHERE enabled = 1").fetchall()
    return {row["rule_key"]: dict(row) for row in rows}


def classify_plan(plan: dict[str, Any], account_cpa: float | None) -> tuple[str, str, int]:
    cost = float(plan.get("cost") or 0)
    conversions = int(plan.get("conversions") or 0)
    cpa = plan.get("cpa")
    if cost >= 180 and conversions == 0:
        return "异常", "消耗较高且暂无转化", 100
    if cpa is not None and account_cpa and cpa >= account_cpa * 1.8:
        return "风险", "CPA明显高于账户平均", 80
    if cost >= 100 and conversions <= 1:
        return "观察", "已有一定消耗，转化偏慢", 55
    if conversions >= 2 and cpa is not None and account_cpa and cpa <= account_cpa * 0.8:
        return "强势", "转化较多且CPA优于账户平均", 10
    return "正常", "指标处于合理范围", 30


def maybe_create_alerts(account_id: int, plan_id: int, current: dict[str, Any], previous: dict[str, Any] | None) -> None:
    rules = _rule_map()
    now = datetime.now(timezone.utc)
    candidates: list[tuple[str, str, str, str]] = []
    cost_delta = float(current["cost"]) - float((previous or {}).get("cost") or 0)
    conv_delta = int(current["conversions"]) - int((previous or {}).get("conversions") or 0)
    if conv_delta > 0:
        candidates.append(("conversion", "positive", "新增转化", f"新增 {conv_delta} 个转化，当前累计 {current['conversions']} 个"))

    high_cost = rules.get("high_cost_no_conversion")
    if high_cost and cost_delta >= float(high_cost["threshold"]) and conv_delta == 0:
        candidates.append(("high_cost_no_conversion", "danger", "高消耗无转化", f"近期新增消耗 ¥{cost_delta:.2f}，暂无新增转化"))

    cpa_rule = rules.get("high_cpa")
    cpa = None if int(current["conversions"]) == 0 else float(current["cost"]) / int(current["conversions"])
    if cpa_rule and cpa is not None and cpa > float(cpa_rule["threshold"]):
        candidates.append(("high_cpa", "danger", "CPA 风险", f"当前 CPA ¥{cpa:.2f}，已超过预警阈值"))

    with connection() as conn:
        for alert_type, severity, title, message in candidates:
            cutoff = (now - timedelta(minutes=5)).isoformat()
            exists = conn.execute(
                """SELECT 1 FROM alerts WHERE account_id=? AND plan_id=? AND type=?
                   AND timestamp>=? LIMIT 1""",
                (account_id, plan_id, alert_type, cutoff),
            ).fetchone()
            if not exists:
                conn.execute(
                    """INSERT INTO alerts(account_id, plan_id, type, severity, title, message, timestamp, read)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
                    (account_id, plan_id, alert_type, severity, title, message, now.isoformat()),
                )

