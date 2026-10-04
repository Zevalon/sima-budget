from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.modules.administration.schemas import RoleAssignmentInput, UserCreateRequest


def test_all_scope_rejects_invalid_scope_name() -> None:
    with pytest.raises(ValidationError):
        RoleAssignmentInput(
            role_id=uuid4(),
            scope_type="INVALID",
            scope_unit_id=None,
        )


def test_user_password_requires_minimum_length() -> None:
    with pytest.raises(ValidationError):
        UserCreateRequest(
            username="tester",
            email=None,
            full_name="Test User",
            password="short",
            primary_unit_id=uuid4(),
            role_assignments=[],
        )
