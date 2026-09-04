from backend.app.config import settings
from backend.app.database import init_database
from backend.app.providers.mock_provider import MockProvider


def test_timeseries_aggregation_uses_raw_snapshots(tmp_path) -> None:
    original = settings.database_url
    settings.database_url = f"sqlite:///{tmp_path / 'test.db'}"
    try:
        init_database()
        provider = MockProvider()
        provider.seed()
        accounts = provider.get_accounts()
        assert len(accounts) == 2
        plans = provider.get_plans(accounts[0]["id"])
        assert [plan["id"] for plan in plans] == [1, 2, 3]
        series = provider.get_timeseries(accounts[0]["id"], "15m", "account")
        assert series
        assert series[-1]["cost"] >= series[0]["cost"]
        assert series[-1]["ctr"] is None or series[-1]["ctr"] >= 0
    finally:
        settings.database_url = original
