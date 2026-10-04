import pytest
from pydantic import ValidationError

from app.modules.budget_plans.schemas import (
    BudgetPlanApproveRequest,
    BudgetPlanRejectRequest,
    BudgetPlanSubmitRequest,
)


def test_submit_requires_positive_expected_row_version() -> None:
    payload = BudgetPlanSubmitRequest(expected_row_version=4)
    assert payload.expected_row_version == 4

    with pytest.raises(ValidationError):
        BudgetPlanSubmitRequest(expected_row_version=0)


def test_approval_decision_identifies_exact_submission_and_version() -> None:
    approve = BudgetPlanApproveRequest(
        expected_row_version=6,
        expected_submission_no=2,
        expected_version_no=2,
        decision_note=None,
    )
    reject = BudgetPlanRejectRequest(
        expected_row_version=6,
        expected_submission_no=2,
        expected_version_no=2,
        reason="Perlu koreksi",
    )

    assert approve.expected_row_version == 6
    assert approve.expected_submission_no == 2
    assert approve.expected_version_no == 2
    assert reject.expected_submission_no == 2
