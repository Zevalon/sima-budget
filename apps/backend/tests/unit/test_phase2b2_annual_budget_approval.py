import pytest
from pydantic import ValidationError

from app.modules.annual_budgets.schemas import (
    AnnualBudgetApproveRequest,
    AnnualBudgetRejectRequest,
)


def test_reject_reason_requires_meaningful_text() -> None:
    with pytest.raises(ValidationError):
        AnnualBudgetRejectRequest(reason="x")


def test_approve_note_is_optional() -> None:
    payload = AnnualBudgetApproveRequest()
    assert payload.decision_note is None
