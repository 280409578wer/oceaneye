from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from typing import Any

from ..database import connection
from ..services.ai_service import AIService
from ..services.alert_service import classify_plan, maybe_create_alerts
from ..services.metrics import enrich_metrics, metric_delta, parse_timestamp
from .base import DataProvider


LOCAL_TZ = timezone(timedelta(hours=8), name="Asia/Shanghai")
INTERVAL_MINUTES = {"5m": 5, "15m": 15, "30m": 30, "1h": 60}


class MockProvider(DataProvider):
    def __init__(self) -> None:
        self.ai_service = AIService()

    def seed(self) -> None:
        now = datetime.now(LOCAL_TZ)
        accounts = [
            ("艺恒", "MOCK-YIHENG", 3821.20),
            ("鼎远", "MOCK-DINGYUAN", 1460.00),
        ]
        plan_specs = {
            "艺恒": [("0902", "stable", 800), ("0903", "normal", 700), ("0904", "risky", 900)],
            "鼎远": [("0901", "stable", 600), ("0902", "normal", 650), ("0903", "risky", 850)],
        }
        with connection() as conn:
            for account_name, advertiser_id, balance in accounts:
                conn.execute(
                    """INSERT OR IGNORE INTO accounts(name, advertiser_id, balance, status, created_at)
                       VALUES (?, ?, ?, 'normal', ?)""",
                    (account_name, advertiser_id, balance, now.isoformat()),
                )
                account_id = conn.execute(
                    "SELECT id FROM accounts WHERE advertiser_id=?", (advertiser_id,)
                ).fetchone()["id"]
                for plan_name, profile, budget in plan_specs[account_name]:
                    conn.execute(
                        """INSERT OR IGNORE INTO plans(account_id, name, status, budget, profile, created_at)
                           VALUES (?, ?, 'active', ?, ?, ?)""",
                        (account_id, plan_name, budget, profile, now.isoformat()),
                    )

        self._seed_today_history()
        self._seed_demo_alerts()

    def _seed_today_history(self) -> None:
        now = datetime.now(LOCAL_TZ)
        start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        if now < start:
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        with connection() as conn:
            existing = conn.execute(
                "SELECT COUNT(*) AS count FROM metrics WHERE timestamp>=?",
                (now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),),
            ).fetchone()["count"]
            plans = [dict(row) for row in conn.execute("SELECT * FROM plans ORDER BY id").fetchall()]
        if existing or not plans:
            return

        states = {plan["id"]: {"cost": 0.0, "impressions": 0, "clicks": 0, "conversions": 0} for plan in plans}
        cursor = start
        rng = random.Random(now.strftime("%Y%m%d"))
        while cursor <= now:
            with connection() as conn:
                for plan in plans:
                    state = states[plan["id"]]
                    self._advance_state(state, plan["profile"], rng, historical=True)
                    conn.execute(
                        """INSERT INTO metrics(account_id, plan_id, timestamp, cost, impressions, clicks, conversions)
                           VALUES (?, ?, ?, ?, ?, ?, ?)""",
                        (
                            plan["account_id"], plan["id"], cursor.isoformat(), round(state["cost"], 2),
                            state["impressions"], state["clicks"], state["conversions"],
                        ),
                    )
            cursor += timedelta(minutes=15)

    @staticmethod
    def _advance_state(state: dict[str, Any], profile: str, rng: random.Random, historical: bool) -> None:
        scale = 1.0 if historical else 0.28
        profile_data = {
            "stable": (9.5, 0.021, 0.015),
            "normal": (11.0, 0.017, 0.008),
            "risky": (15.5, 0.010, 0.001),
        }
        base_cost, ctr, conversion_rate = profile_data.get(profile, profile_data["normal"])
        cost_add = max(0.6, rng.uniform(base_cost * 0.72, base_cost * 1.35) * scale)
        impressions_add = max(35, int(cost_add * rng.uniform(52, 72)))
        clicks_add = max(0, int(impressions_add * max(0.004, rng.gauss(ctr, ctr * 0.15))))
        conversions_add = sum(1 for _ in range(clicks_add) if rng.random() < conversion_rate)
        state["cost"] += cost_add
        state["impressions"] += impressions_add
        state["clicks"] += clicks_add
        state["conversions"] += conversions_add

    def tick(self) -> None:
        rng = random.Random()
        with connection() as conn:
            plans = [dict(row) for row in conn.execute("SELECT * FROM plans WHERE status='active'").fetchall()]
        for plan in plans:
            with connection() as conn:
                previous_row = conn.execute(
                    "SELECT * FROM metrics WHERE plan_id=? ORDER BY timestamp DESC LIMIT 1", (plan["id"],)
                ).fetchone()
                previous = dict(previous_row) if previous_row else {
                    "cost": 0.0, "impressions": 0, "clicks": 0, "conversions": 0
                }
                state = {
                    "cost": float(previous["cost"]), "impressions": int(previous["impressions"]),
                    "clicks": int(previous["clicks"]), "conversions": int(previous["conversions"]),
                }
                self._advance_state(state, plan["profile"], rng, historical=False)
                now = datetime.now(LOCAL_TZ).isoformat()
                conn.execute(
                    """INSERT INTO metrics(account_id, plan_id, timestamp, cost, impressions, clicks, conversions)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (plan["account_id"], plan["id"], now, round(state["cost"], 2), state["impressions"],
                     state["clicks"], state["conversions"]),
                )
            maybe_create_alerts(plan["account_id"], plan["id"], state, previous)

    def _seed_demo_alerts(self) -> None:
        with connection() as conn:
            if conn.execute("SELECT COUNT(*) AS count FROM alerts").fetchone()["count"]:
                return
            plans = conn.execute("SELECT id, account_id, name FROM plans ORDER BY id LIMIT 3").fetchall()
            now = datetime.now(LOCAL_TZ)
            examples = [
                ("conversion", "positive", "新增转化", "新增 1 个转化，投放效率正在改善"),
                ("spend_spike", "warning", "消耗异动", "最近30分钟消耗增长较快，请继续观察"),
                ("high_cpa", "danger", "CPA 风险", "CPA 高于账户均值，建议重点关注"),
            ]
            for index, plan in enumerate(plans):
                alert_type, severity, title, message = examples[index]
                conn.execute(
                    """INSERT INTO alerts(account_id, plan_id, type, severity, title, message, timestamp, read)
                       VALUES (?, ?, ?, ?, ?, ?, ?, 0)""",
                    (plan["account_id"], plan["id"], alert_type, severity, title, message,
                     (now - timedelta(minutes=index * 7 + 2)).isoformat()),
                )

    @staticmethod
    def _snapshot_at(account_id: int, when: datetime | None = None) -> dict[str, float]:
        with connection() as conn:
            plans = conn.execute("SELECT id FROM plans WHERE account_id=?", (account_id,)).fetchall()
            totals = {"cost": 0.0, "impressions": 0, "clicks": 0, "conversions": 0}
            for plan in plans:
                if when:
                    row = conn.execute(
                        "SELECT * FROM metrics WHERE plan_id=? AND timestamp<=? ORDER BY timestamp DESC LIMIT 1",
                        (plan["id"], when.isoformat()),
                    ).fetchone()
                else:
                    row = conn.execute(
                        "SELECT * FROM metrics WHERE plan_id=? ORDER BY timestamp DESC LIMIT 1", (plan["id"],)
                    ).fetchone()
                if row:
                    for key in totals:
                        totals[key] += row[key]
        return totals

    def get_accounts(self) -> list[dict[str, Any]]:
        with connection() as conn:
            rows = [dict(row) for row in conn.execute("SELECT * FROM accounts ORDER BY id").fetchall()]
        result = []
        for row in rows:
            summary = self.get_account_summary(row["id"])
            result.append({**row, **{key: summary[key] for key in ("cost", "conversions", "cpa", "ctr")}})
        return result

    def get_account(self, account_id: int) -> dict[str, Any] | None:
        with connection() as conn:
            row = conn.execute("SELECT * FROM accounts WHERE id=?", (account_id,)).fetchone()
        return dict(row) if row else None

    def get_account_summary(self, account_id: int) -> dict[str, Any]:
        now = datetime.now(LOCAL_TZ)
        total = enrich_metrics(self._snapshot_at(account_id))
        at_30 = self._snapshot_at(account_id, now - timedelta(minutes=30))
        at_60 = self._snapshot_at(account_id, now - timedelta(minutes=60))
        current_window = enrich_metrics({key: total[key] - at_30[key] for key in ("cost", "impressions", "clicks", "conversions")})
        previous_window = enrich_metrics({key: at_30[key] - at_60[key] for key in ("cost", "impressions", "clicks", "conversions")})
        account = self.get_account(account_id)
        if not account:
            raise KeyError("账户不存在")
        with connection() as conn:
            budget = conn.execute("SELECT COALESCE(SUM(budget), 0) AS total FROM plans WHERE account_id=?", (account_id,)).fetchone()["total"]
            latest = conn.execute("SELECT MAX(timestamp) AS timestamp FROM metrics WHERE account_id=?", (account_id,)).fetchone()["timestamp"]
        deltas = {
            key: metric_delta(current_window.get(key), previous_window.get(key), inverse_good=key == "cpa")
            for key in ("cost", "impressions", "clicks", "conversions", "ctr", "cvr", "cpa")
        }
        return {
            **total,
            "balance": round(float(account["balance"]), 2),
            "budget": round(float(budget), 2),
            "budget_usage": round((total["cost"] / budget) * 100, 1) if budget else None,
            "last_updated": latest,
            "comparison_window": "最近30分钟 vs 上一30分钟",
            "deltas": deltas,
        }

    def get_plans(self, account_id: int) -> list[dict[str, Any]]:
        with connection() as conn:
            plans = [dict(row) for row in conn.execute("SELECT * FROM plans WHERE account_id=? ORDER BY id", (account_id,)).fetchall()]
            latest_rows = {}
            for plan in plans:
                row = conn.execute("SELECT * FROM metrics WHERE plan_id=? ORDER BY timestamp DESC LIMIT 1", (plan["id"],)).fetchone()
                latest_rows[plan["id"]] = dict(row) if row else {}
        account_cpa = self.get_account_summary(account_id).get("cpa")
        result = []
        for plan in plans:
            enriched = enrich_metrics(latest_rows[plan["id"]])
            status_label, status_reason, risk_score = classify_plan(enriched, account_cpa)
            result.append({**enriched, **plan, "status_label": status_label, "status_reason": status_reason, "risk_score": risk_score})
        return result

    def get_plan_metrics(self, plan_id: int) -> dict[str, Any]:
        with connection() as conn:
            plan_row = conn.execute(
                """SELECT p.*, a.name AS account_name FROM plans p
                   JOIN accounts a ON a.id=p.account_id WHERE p.id=?""", (plan_id,)
            ).fetchone()
            metric_row = conn.execute("SELECT * FROM metrics WHERE plan_id=? ORDER BY timestamp DESC LIMIT 1", (plan_id,)).fetchone()
        if not plan_row:
            raise KeyError("计划不存在")
        plan = dict(plan_row)
        enriched = enrich_metrics(dict(metric_row) if metric_row else {})
        account_cpa = self.get_account_summary(plan["account_id"]).get("cpa")
        status_label, status_reason, risk_score = classify_plan(enriched, account_cpa)
        return {**enriched, **plan, "status_label": status_label, "status_reason": status_reason, "risk_score": risk_score}

    def get_timeseries(self, entity_id: int, interval: str, entity_type: str = "account") -> list[dict[str, Any]]:
        minutes = INTERVAL_MINUTES.get(interval)
        if minutes is None:
            raise ValueError("interval 仅支持 5m、15m、30m、1h")
        start = datetime.now(LOCAL_TZ).replace(hour=0, minute=0, second=0, microsecond=0)
        with connection() as conn:
            if entity_type == "account":
                rows = [dict(row) for row in conn.execute(
                    "SELECT * FROM metrics WHERE account_id=? AND timestamp>=? ORDER BY timestamp",
                    (entity_id, start.isoformat()),
                ).fetchall()]
            else:
                rows = [dict(row) for row in conn.execute(
                    "SELECT * FROM metrics WHERE plan_id=? AND timestamp>=? ORDER BY timestamp",
                    (entity_id, start.isoformat()),
                ).fetchall()]
        buckets: dict[datetime, dict[int, dict[str, Any]]] = {}
        for row in rows:
            stamp = parse_timestamp(row["timestamp"]).astimezone(LOCAL_TZ)
            bucket_minute = (stamp.minute // minutes) * minutes if minutes < 60 else 0
            bucket = stamp.replace(minute=bucket_minute, second=0, microsecond=0)
            buckets.setdefault(bucket, {})[int(row["plan_id"])] = row
        carried: dict[int, dict[str, Any]] = {}
        result = []
        for bucket in sorted(buckets):
            carried.update(buckets[bucket])
            totals = {"cost": 0.0, "impressions": 0, "clicks": 0, "conversions": 0}
            for row in carried.values():
                for key in totals:
                    totals[key] += row[key]
            result.append({"timestamp": bucket.isoformat(), **enrich_metrics(totals)})
        return result

    def get_balance(self, account_id: int) -> float:
        account = self.get_account(account_id)
        if not account:
            raise KeyError("账户不存在")
        return float(account["balance"])

    def get_ai_analysis(self, account_id: int) -> str:
        account = self.get_account(account_id)
        if not account:
            raise KeyError("账户不存在")
        return self.ai_service.analyze(account, self.get_account_summary(account_id), self.get_plans(account_id))
