from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.unit_allocations.schemas import (
    UnitAllocationCreateRequest,
    UnitAllocationUpdateRequest,
)


def test_unit_allocation_amount_uses_decimal() -> None:
    payload = UnitAllocationCreateRequest(
        fiscal_year_id=uuid4(),
        organization_unit_id=uuid4(),
        amount=Decimal("25000000000.25"),
    )
    assert payload.amount == Decimal("25000000000.25")


def test_unit_allocation_rejects_zero_amount() -> None:
    with pytest.raises(ValidationError):
        UnitAllocationCreateRequest(
            fiscal_year_id=uuid4(),
            organization_unit_id=uuid4(),
            amount=Decimal("0"),
        )


def test_unit_allocation_update_can_change_notes_only() -> None:
    payload = UnitAllocationUpdateRequest(
        expected_version=1,
        notes="Penyesuaian alokasi",
    )
    assert payload.expected_version == 1
    assert payload.amount is None
    assert payload.notes == "Penyesuaian alokasi"
