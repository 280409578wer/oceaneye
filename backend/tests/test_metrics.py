from backend.app.services.alert_service import classify_plan
from backend.app.services.metrics import enrich_metrics, safe_ratio


def test_safe_ratio_handles_zero() -> None:
    assert safe_ratio(10, 0) is None
    assert safe_ratio(0, 0) is None


def test_derived_metrics() -> None:
    result = enrich_metrics({"cost": 120, "impressions": 1000, "clicks": 20, "conversions": 2})
    assert result["ctr"] == 2.0
    assert result["cvr"] == 10.0
    assert result["cpa"] == 60.0


def test_plan_status_rule() -> None:
    label, _, score = classify_plan({"cost": 220, "conversions": 0, "cpa": None}, 80)
    assert label == "异常"
    assert score == 100

