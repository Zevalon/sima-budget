from app.core.security import (
    csrf_token_matches,
    derive_csrf_token,
    generate_session_token,
    hash_session_token,
)


def test_session_tokens_are_random_and_hashable() -> None:
    first = generate_session_token()
    second = generate_session_token()

    assert first != second
    assert len(first) >= 48
    assert hash_session_token(first, "secret-a") == hash_session_token(first, "secret-a")
    assert hash_session_token(first, "secret-a") != hash_session_token(first, "secret-b")


def test_csrf_token_is_bound_to_session_and_secret() -> None:
    raw_session = generate_session_token()
    csrf = derive_csrf_token(raw_session, "csrf-secret")

    assert csrf_token_matches(raw_session, csrf, "csrf-secret")
    assert not csrf_token_matches(raw_session, csrf, "different-secret")
    assert not csrf_token_matches(generate_session_token(), csrf, "csrf-secret")
