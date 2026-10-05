from types import SimpleNamespace
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.realizations.schemas import RealizationStatus
from app.modules.realizations.service import _assert_workflow_identity


def test_workflow_identity_accepts_exact_snapshot() -> None:
    plan_version_id = uuid4()
    item = SimpleNamespace(
        row_version=4,
        status="POSTED",
        plan_version_id=plan_version_id,
    )

    _assert_workflow_identity(
        item,  # type: ignore[arg-type]
        expected_row_version=4,
        expected_status=RealizationStatus.POSTED,
        expected_plan_version_id=plan_version_id,
        action_label="reversal",
    )


@pytest.mark.parametrize("field", ["row_version", "status", "plan_version"])
def test_workflow_identity_rejects_stale_snapshot(field: str) -> None:
    plan_version_id = uuid4()
    item = SimpleNamespace(
        row_version=4,
        status="DRAFT",
        plan_version_id=plan_version_id,
    )
    expected_row_version = 4
    expected_status = RealizationStatus.DRAFT
    expected_plan_version_id = plan_version_id

    if field == "row_version":
        expected_row_version = 3
    elif field == "status":
        expected_status = RealizationStatus.POSTED
    else:
        expected_plan_version_id = uuid4()

    with pytest.raises(HTTPException) as error:
        _assert_workflow_identity(
            item,  # type: ignore[arg-type]
            expected_row_version=expected_row_version,
            expected_status=expected_status,
            expected_plan_version_id=expected_plan_version_id,
            action_label="melanjutkan",
        )

    assert error.value.status_code == 409
