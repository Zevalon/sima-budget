from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.realizations.schemas import (
    RealizationCreateRequest,
    RealizationPostRequest,
    RealizationStatus,
    RealizationUpdateRequest,
)
from app.modules.realizations.service import normalize_money


def test_realization_money_uses_half_up_rounding() -> None:
    assert normalize_money(Decimal("10.005")) == Decimal("10.01")


def test_realization_amount_must_be_positive() -> None:
    with pytest.raises(ValidationError):
        RealizationCreateRequest(
            budget_plan_id=uuid4(),
            realization_date=date(2026, 1, 10),
            reference_number="DOC-001",
            description="Invalid",
            amount=Decimal("0.00"),
        )


def test_realization_mutations_require_expected_identity() -> None:
    plan_version_id = uuid4()
    update = RealizationUpdateRequest(
        expected_row_version=2,
        expected_status=RealizationStatus.DRAFT,
        expected_plan_version_id=plan_version_id,
        realization_date=date(2026, 2, 1),
        reference_number="DOC-002",
        description="Update",
        vendor_name=None,
        amount=Decimal("100.00"),
    )
    post = RealizationPostRequest(
        expected_row_version=2,
        expected_status=RealizationStatus.DRAFT,
        expected_plan_version_id=plan_version_id,
    )
    assert update.expected_row_version == 2
    assert update.expected_status.value == "DRAFT"
    assert post.expected_plan_version_id == plan_version_id
