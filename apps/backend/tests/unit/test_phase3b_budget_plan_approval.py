from app.modules.budget_plans.schemas import (
    BudgetPlanApprovalStatus,
    BudgetPlanApproveRequest,
    BudgetPlanRejectRequest,
)


def test_budget_plan_approval_status_values_are_stable() -> None:
    assert [item.value for item in BudgetPlanApprovalStatus] == [
        "PENDING",
        "APPROVED",
        "REJECTED",
    ]


def test_budget_plan_approval_payloads_validate() -> None:
    approve = BudgetPlanApproveRequest(
        expected_row_version=3,
        expected_submission_no=2,
        expected_version_no=2,
        decision_note="Sesuai rencana unit",
    )
    reject = BudgetPlanRejectRequest(
        expected_row_version=3,
        expected_submission_no=2,
        expected_version_no=2,
        reason="Perbaiki rincian",
    )
    assert approve.expected_submission_no == 2
    assert approve.decision_note == "Sesuai rencana unit"
    assert reject.expected_version_no == 2
    assert reject.reason == "Perbaiki rincian"
