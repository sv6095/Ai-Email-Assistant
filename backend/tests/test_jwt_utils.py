import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from fastapi import HTTPException

from utils.jwt import get_current_user


def make_token(secret: str, payload_extra: dict = None, expires_in_seconds: int = 3600):
    now = datetime.now(timezone.utc)
    payload = {
        "sub": "user-123",
        "email": "user@example.com",
        "exp": int((now + timedelta(seconds=expires_in_seconds)).timestamp()),
    }
    if payload_extra:
        payload.update(payload_extra)
    return jwt.encode(payload, secret, algorithm="HS256")


def test_get_current_user_decodes_valid_token(monkeypatch):
    secret = "test-secret-key"
    monkeypatch.setenv("JWT_SECRET_KEY", secret)

    token = make_token(secret)
    authorization_header = f"Bearer {token}"

    user = get_current_user(authorization=authorization_header)

    assert user["email"] == "user@example.com"
    assert user["sub"] == "user-123"


def test_get_current_user_rejects_missing_header():
    try:
        get_current_user(authorization=None)
    except HTTPException as exc:
        assert exc.status_code == 401
        assert "Missing or invalid authorization header" in exc.detail
    else:
        assert False, "Expected HTTPException for missing header"


def test_get_current_user_rejects_expired_token(monkeypatch):
    secret = "test-secret-key"
    monkeypatch.setenv("JWT_SECRET_KEY", secret)

    # Token expired 1 second ago
    token = make_token(secret, expires_in_seconds=-1)
    authorization_header = f"Bearer {token}"

    try:
        get_current_user(authorization=authorization_header)
    except HTTPException as exc:
        assert exc.status_code == 401
        assert "Token expired" in exc.detail
    else:
        assert False, "Expected HTTPException for expired token"


