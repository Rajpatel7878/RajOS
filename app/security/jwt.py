import os
from datetime import datetime, timedelta, timezone
from jose import jwt

# SECRET_KEY must be set via environment variable; never hardcode.
# Generate with: python -c "import secrets; print(secrets.token_urlsafe(48))"
SECRET_KEY = None  # Will be set at runtime from environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10080   # 7 days
REFRESH_TOKEN_EXPIRE_DAYS = 30        # 30 days


def _secret_key(secret_key: str | None = None) -> str:
    key = secret_key or SECRET_KEY or os.getenv("SECRET_KEY")
    if not key:
        raise ValueError("SECRET_KEY must be set in environment or passed to the token factory")
    return key


def _create_token(data: dict, lifetime: timedelta, token_type: str, secret_key: str | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + lifetime
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, _secret_key(secret_key), algorithm=ALGORITHM)


def create_access_token(data: dict, secret_key: str | None = None):
    """Short-lived token used to authenticate API requests."""
    return _create_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES), "access", secret_key)


def create_refresh_token(data: dict, secret_key: str | None = None):
    """Long-lived token that can mint new access tokens without a password."""
    return _create_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS), "refresh", secret_key)
