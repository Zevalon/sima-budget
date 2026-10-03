from app.core.security import hash_password, verify_password


def test_password_hash_roundtrip() -> None:
    raw = "Correct-Horse-Battery-Staple-123!"
    hashed = hash_password(raw)
    assert raw != hashed
    assert verify_password(hashed, raw)
    assert not verify_password(hashed, "wrong-password")
