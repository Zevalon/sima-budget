import hashlib
import hmac
import secrets
from dataclasses import dataclass

from argon2 import PasswordHasher

_password_hasher = PasswordHasher()


@dataclass(frozen=True, slots=True)
class CookiePolicy:
    http_only: bool = True
    same_site: str = "lax"
    secure: bool = False


def hash_password(password: str) -> str:
    return _password_hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _password_hasher.verify(password_hash, password)
    except Exception:  # noqa: BLE001 - invalid credentials intentionally collapse to False
        return False


def generate_session_token() -> str:
    return secrets.token_urlsafe(48)


def hash_session_token(raw_token: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        raw_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def derive_csrf_token(raw_session_token: str, secret: str) -> str:
    return hmac.new(
        secret.encode("utf-8"),
        raw_session_token.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def csrf_token_matches(raw_session_token: str, submitted_token: str, secret: str) -> bool:
    expected = derive_csrf_token(raw_session_token, secret)
    return hmac.compare_digest(expected, submitted_token)
