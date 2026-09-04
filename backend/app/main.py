from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .config import settings
from .database import connection, init_database
from .providers.mock_provider import INTERVAL_MINUTES, MockProvider


provider = MockProvider()


async def mock_loop() -> None:
    while True:
        await asyncio.sleep(max(5, settings.mock_interval_seconds))
        await asyncio.to_thread(provider.tick)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_database()
    if settings.data_source == "mock":
        await asyncio.to_thread(provider.seed)
    task = None
    if settings.data_source == "mock" and settings.mock_enabled:
        task = asyncio.create_task(mock_loop())
    yield
    if task:
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task


app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SettingsUpdate(BaseModel):
    refresh_interval: int | None = None
    auto_refresh: bool | None = None
    alert_rules: list[dict[str, Any]] | None = None


def safe_call(callback):
    try:
        return callback()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "data_source": settings.data_source, "server_time": datetime.now(timezone.utc).isoformat()}


@app.get("/api/accounts")
def accounts():
    return provider.get_accounts()


@app.get("/api/accounts/{account_id}")
def account(account_id: int):
    result = provider.get_account(account_id)
    if not result:
        raise HTTPException(status_code=404, detail="账户不存在")
    return result


@app.get("/api/accounts/{account_id}/summary")
def account_summary(account_id: int):
    return safe_call(lambda: provider.get_account_summary(account_id))


@app.get("/api/accounts/{account_id}/timeseries")
def account_timeseries(account_id: int, interval: str = Query("15m")):
    return safe_call(lambda: provider.get_timeseries(account_id, interval, "account"))


@app.get("/api/accounts/{account_id}/plans")
def account_plans(account_id: int):
    return safe_call(lambda: provider.get_plans(account_id))


@app.get("/api/accounts/{account_id}/analysis")
def account_analysis(account_id: int):
    return {"text": safe_call(lambda: provider.get_ai_analysis(account_id)), "provider": "rules"}


@app.get("/api/plans/{plan_id}")
def plan(plan_id: int):
    return safe_call(lambda: provider.get_plan_metrics(plan_id))


@app.get("/api/plans/{plan_id}/timeseries")
def plan_timeseries(plan_id: int, interval: str = Query("15m")):
    return safe_call(lambda: provider.get_timeseries(plan_id, interval, "plan"))


@app.get("/api/alerts")
def alerts(account_id: int | None = None, limit: int = Query(30, ge=1, le=200)):
    with connection() as conn:
        params: list[Any] = []
        where = ""
        if account_id is not None:
            where = "WHERE al.account_id=?"
            params.append(account_id)
        params.append(limit)
        rows = conn.execute(
            f"""SELECT al.*, p.name AS plan_name, a.name AS account_name
                FROM alerts al JOIN accounts a ON a.id=al.account_id
                LEFT JOIN plans p ON p.id=al.plan_id {where}
                ORDER BY al.timestamp DESC LIMIT ?""",
            params,
        ).fetchall()
    return [dict(row) for row in rows]


@app.get("/api/settings")
def get_settings():
    with connection() as conn:
        values = {row["key"]: row["value"] for row in conn.execute("SELECT * FROM settings").fetchall()}
        rules = [dict(row) for row in conn.execute("SELECT * FROM alert_rules ORDER BY id").fetchall()]
    return {"values": values, "alert_rules": rules, "data_source": settings.data_source}


@app.put("/api/settings")
def update_settings(payload: SettingsUpdate):
    now = datetime.now(timezone.utc).isoformat()
    with connection() as conn:
        values: dict[str, str] = {}
        if payload.refresh_interval is not None:
            if payload.refresh_interval not in {10, 30, 60, 300, 900}:
                raise HTTPException(status_code=400, detail="刷新周期不受支持")
            values["refresh_interval"] = str(payload.refresh_interval)
        if payload.auto_refresh is not None:
            values["auto_refresh"] = str(payload.auto_refresh).lower()
        for key, value in values.items():
            conn.execute(
                """INSERT INTO settings(key, value, updated_at) VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
                (key, value, now),
            )
        if payload.alert_rules:
            for rule in payload.alert_rules:
                if not {"rule_key", "enabled", "threshold"}.issubset(rule):
                    raise HTTPException(status_code=400, detail="预警规则字段不完整")
                conn.execute(
                    """UPDATE alert_rules SET enabled=?, threshold=?, window_minutes=? WHERE rule_key=?""",
                    (int(bool(rule["enabled"])), float(rule["threshold"]), int(rule.get("window_minutes", 30)), rule["rule_key"]),
                )
    return get_settings()


if __name__ == "__main__":
    init_database()
    provider.seed()
    print("OceanEye 数据库初始化完成")

