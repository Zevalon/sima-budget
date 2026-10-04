import pytest
from pydantic import ValidationError

from app.modules.realizations.schemas import (
    RealizationCorrectionRequest,
    RealizationStatusActionRequest,
)


def test_realization_status_action_requires_meaningful_reason() -> None:
    with pytest.raises(ValidationError):
        RealizationStatusActionRequest(expected_row_version=2, reason="x")
    with pytest.raises(ValidationError):
        RealizationStatusActionRequest(expected_row_version=2, reason="   ")


def test_realization_status_action_keeps_expected_version() -> None:
    payload = RealizationStatusActionRequest(
        expected_row_version=4,
        reason="Dokumen dibatalkan karena sumber transaksi berubah.",
    )
    assert payload.expected_row_version == 4


def test_correction_request_requires_expected_version() -> None:
    payload = RealizationCorrectionRequest(expected_row_version=3)
    assert payload.expected_row_version == 3
