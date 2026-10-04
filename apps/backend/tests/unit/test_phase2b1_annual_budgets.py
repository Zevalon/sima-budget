from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.annual_budgets.schemas import (
    AnnualBudgetCreateRequest,
    AnnualBudgetStatus,
)


def test_annual_budget_amount_uses_decimal() -> None:
    payload = AnnualBudgetCreateRequest(
        fiscal_year_id=uuid4(),
        amount=Decimal("500000000000.25"),
        notes="Pagu tahunan",
    )
    assert payload.amount == Decimal("500000000000.25")


def test_annual_budget_rejects_non_positive_amount() -> None:
    with pytest.raises(ValidationError):
        AnnualBudgetCreateRequest(
            fiscal_year_id=uuid4(),
            amount=Decimal("0"),
        )


def test_annual_budget_status_contract() -> None:
    assert AnnualBudgetStatus.DRAFT.value == "DRAFT"
    assert AnnualBudgetStatus.PENDING_APPROVAL.value == "PENDING_APPROVAL"
