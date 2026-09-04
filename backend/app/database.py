from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

from .config import settings


def _database_path() -> Path:
    prefix = "sqlite:///"
    if not settings.database_url.startswith(prefix):
        raise ValueError("V0.1 仅支持 SQLite DATABASE_URL")
    path = Path(settings.database_url.removeprefix(prefix))
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_database_path(), timeout=20)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


SCHEMA = """
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    advertiser_id TEXT NOT NULL UNIQUE,
    balance REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'normal',
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    budget REAL NOT NULL DEFAULT 0,
    profile TEXT NOT NULL DEFAULT 'normal',
    created_at TEXT NOT NULL,
    UNIQUE(account_id, name)
);

CREATE TABLE IF NOT EXISTS metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    plan_id INTEGER NOT NULL REFERENCES plans(id),
    timestamp TEXT NOT NULL,
    cost REAL NOT NULL DEFAULT 0,
    impressions INTEGER NOT NULL DEFAULT 0,
    clicks INTEGER NOT NULL DEFAULT 0,
    conversions INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_metrics_plan_time ON metrics(plan_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_metrics_account_time ON metrics(account_id, timestamp);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts(id),
    plan_id INTEGER REFERENCES plans(id),
    type TEXT NOT NULL,
    severity TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    read INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_alerts_account_time ON alerts(account_id, timestamp DESC);

CREATE TABLE IF NOT EXISTS alert_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_key TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    enabled INTEGER NOT NULL DEFAULT 1,
    threshold REAL NOT NULL,
    window_minutes INTEGER NOT NULL DEFAULT 30,
    config_json TEXT NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def init_database() -> None:
    with connection() as conn:
        conn.executescript(SCHEMA)
        now = datetime.now(timezone.utc).isoformat()
        rules = [
            ("high_cost_no_conversion", "高消耗无转化", 1, 100.0, 30),
            ("high_cpa", "CPA过高", 1, 150.0, 30),
            ("low_balance", "余额不足", 1, 500.0, 30),
            ("spend_spike", "突然爆量", 1, 100.0, 30),
        ]
        conn.executemany(
            """INSERT OR IGNORE INTO alert_rules
               (rule_key, name, enabled, threshold, window_minutes)
               VALUES (?, ?, ?, ?, ?)""",
            rules,
        )
        defaults = {
            "refresh_interval": "10",
            "auto_refresh": "true",
            "last_account_id": "1",
            "data_version": "1",
        }
        conn.executemany(
            "INSERT OR IGNORE INTO settings(key, value, updated_at) VALUES (?, ?, ?)",
            [(key, value, now) for key, value in defaults.items()],
        )

