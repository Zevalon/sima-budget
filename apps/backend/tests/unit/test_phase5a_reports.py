from decimal import Decimal

from app.modules.reports.service import normalize_amount, utilization_percent


def test_report_amount_normalization_uses_financial_rounding() -> None:
    assert normalize_amount(Decimal("12.345")) == Decimal("12.35")


def test_report_utilization_percent() -> None:
    assert utilization_percent(Decimal("400.00"), Decimal("1000.00")) == Decimal("40.00")
    assert utilization_percent(Decimal("0.00"), Decimal("0.00")) == Decimal("0.00")
