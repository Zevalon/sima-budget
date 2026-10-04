from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.budget_plans.schemas import BudgetPlanItemRequest
from app.modules.budget_plans.service import item_amount


def test_budget_plan_item_amount_uses_decimal_precision() -> None:
    item = BudgetPlanItemRequest(
        budget_category_id=uuid4(),
        unit_of_measure_id=uuid4(),
        description="Cloud service",
        quantity=Decimal("2.5000"),
        unit_price=Decimal("123.45"),
    )
    assert item_amount(item) == Decimal("308.63")


def test_budget_plan_item_rejects_non_positive_quantity() -> None:
    with pytest.raises(ValidationError):
        BudgetPlanItemRequest(
            budget_category_id=uuid4(),
            unit_of_measure_id=uuid4(),
            description="Invalid",
            quantity=Decimal("0"),
            unit_price=Decimal("100.00"),
        )
