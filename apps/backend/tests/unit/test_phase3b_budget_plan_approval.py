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
    approve = BudgetPlanApproveRequest(decision_note="Sesuai rencana unit")
    reject = BudgetPlanRejectRequest(reason="Perbaiki rincian")
    assert approve.decision_note == "Sesuai rencana unit"
    assert reject.reason == "Perbaiki rincian"
