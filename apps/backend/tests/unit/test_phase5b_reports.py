from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.modules.reports.service import resolve_requested_scope


def test_report_unit_filter_keeps_permitted_unit() -> None:
    unit_a = uuid4()
    unit_b = uuid4()

    assert resolve_requested_scope({unit_a, unit_b}, unit_b) == {unit_b}


def test_report_unit_filter_rejects_unit_outside_scope() -> None:
    allowed = uuid4()

    with pytest.raises(HTTPException) as error:
        resolve_requested_scope({allowed}, uuid4())

    assert error.value.status_code == 403
