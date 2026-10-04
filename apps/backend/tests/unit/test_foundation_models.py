from app.core.database import Base
from app.modules.roles.bootstrap_data import ALL_BOOTSTRAP_PERMISSIONS, DEFAULT_ROLE_TEMPLATES
from app.modules.roles.constants import ScopeType
from app.shared.db.model_registry import MODELS

EXPECTED_FOUNDATION_TABLES = {
    "organizations",
    "application_settings",
    "organization_unit_types",
    "organization_units",
    "users",
    "user_unit_memberships",
    "roles",
    "permissions",
    "role_permissions",
    "user_role_assignments",
    "user_sessions",
    "audit_logs",
}


def test_foundation_models_registered() -> None:
    assert MODELS
    assert EXPECTED_FOUNDATION_TABLES.issubset(Base.metadata.tables)


def test_scope_types_are_stable() -> None:
    assert {scope.value for scope in ScopeType} == {
        "OWN",
        "OWN_UNIT",
        "OWN_UNIT_AND_CHILDREN",
        "ALL",
    }


def test_bootstrap_codes_are_unique() -> None:
    permission_codes = [code for code, _, _ in ALL_BOOTSTRAP_PERMISSIONS]
    role_codes = [code for code, _, _, _ in DEFAULT_ROLE_TEMPLATES]

    assert len(permission_codes) == len(set(permission_codes))
    assert len(role_codes) == len(set(role_codes))
