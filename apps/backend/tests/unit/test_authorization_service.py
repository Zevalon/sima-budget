from app.modules.authorization.dependencies import RequirePermission


def test_require_permission_keeps_requested_code() -> None:
    dependency = RequirePermission("users.view")
    assert dependency.permission_code == "users.view"
