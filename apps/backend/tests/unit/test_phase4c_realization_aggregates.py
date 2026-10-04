from decimal import Decimal

from app.modules.realizations.service import utilization_percent


def test_utilization_percent_uses_decimal_precision() -> None:
    assert utilization_percent(Decimal("250.00"), Decimal("1000.00")) == Decimal("25.00")


def test_utilization_percent_handles_zero_approved_amount() -> None:
    assert utilization_percent(Decimal("0.00"), Decimal("0.00")) == Decimal("0.00")
