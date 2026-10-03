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
