from datetime import date

import pytest
from pydantic import ValidationError

from app.core.database import Base
from app.modules.budget_foundation.schemas import FiscalYearCreateRequest, FiscalYearStatus
from app.modules.roles.bootstrap_data import DEFAULT_ROLE_TEMPLATES
from app.shared.db.model_registry import MODELS


def test_phase2a_models_registered() -> None:
    assert MODELS
    assert {"fiscal_years", "budget_categories", "units_of_measure"} <= set(Base.metadata.tables)


def test_fiscal_year_statuses_are_stable() -> None:
    assert {status.value for status in FiscalYearStatus} == {
        "DRAFT",
        "PLANNING",
        "ACTIVE",
        "CLOSED",
        "ARCHIVED",
    }


def test_fiscal_year_dates_must_be_ordered() -> None:
    with pytest.raises(ValidationError):
        FiscalYearCreateRequest(
            code="FY2099",
            year=2099,
            start_date=date(2099, 12, 31),
            end_date=date(2099, 1, 1),
        )


def test_phase2a_authority_separation() -> None:
    roles = {code: permission_codes for code, _, _, permission_codes in DEFAULT_ROLE_TEMPLATES}

    assert "fiscal_years.view" in roles["SYSTEM_ADMIN"]
    assert "fiscal_years.transition" not in roles["SYSTEM_ADMIN"]
    assert "budget_categories.manage" not in roles["SYSTEM_ADMIN"]

    assert "fiscal_years.transition" in roles["BUDGET_ADMIN"]
    assert "fiscal_years.reopen" in roles["BUDGET_ADMIN"]
    assert "budget_categories.manage" in roles["BUDGET_ADMIN"]
    assert "units_of_measure.manage" in roles["BUDGET_ADMIN"]
