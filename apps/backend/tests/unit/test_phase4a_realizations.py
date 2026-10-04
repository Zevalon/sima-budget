from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.realizations.schemas import (
    RealizationCreateRequest,
    RealizationPostRequest,
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


def test_realization_mutations_require_expected_version() -> None:
    update = RealizationUpdateRequest(
        expected_row_version=2,
        realization_date=date(2026, 2, 1),
        reference_number="DOC-002",
        description="Update",
        vendor_name=None,
        amount=Decimal("100.00"),
    )
    post = RealizationPostRequest(expected_row_version=2)
    assert update.expected_row_version == 2
    assert post.expected_row_version == 2
