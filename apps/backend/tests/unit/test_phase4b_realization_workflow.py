from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.realizations.schemas import (
    RealizationCorrectionRequest,
    RealizationStatus,
    RealizationStatusActionRequest,
)


def test_realization_status_action_requires_meaningful_reason() -> None:
    with pytest.raises(ValidationError):
        RealizationStatusActionRequest(
            expected_row_version=2,
            expected_status=RealizationStatus.DRAFT,
            expected_plan_version_id=uuid4(),
            reason="x",
        )
    with pytest.raises(ValidationError):
        RealizationStatusActionRequest(
            expected_row_version=2,
            expected_status=RealizationStatus.DRAFT,
            expected_plan_version_id=uuid4(),
            reason="   ",
        )


def test_realization_status_action_keeps_expected_identity() -> None:
    plan_version_id = uuid4()
    payload = RealizationStatusActionRequest(
        expected_row_version=4,
        expected_status=RealizationStatus.DRAFT,
        expected_plan_version_id=plan_version_id,
        reason="Dokumen dibatalkan karena sumber transaksi berubah.",
    )
    assert payload.expected_row_version == 4
    assert payload.expected_status.value == "DRAFT"
    assert payload.expected_plan_version_id == plan_version_id


def test_correction_request_requires_expected_identity() -> None:
    plan_version_id = uuid4()
    payload = RealizationCorrectionRequest(
        expected_row_version=3,
        expected_status=RealizationStatus.REVERSED,
        expected_plan_version_id=plan_version_id,
    )
    assert payload.expected_row_version == 3
    assert payload.expected_status.value == "REVERSED"
    assert payload.expected_plan_version_id == plan_version_id
