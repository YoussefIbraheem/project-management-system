import time

import jwt
import pytest

from app.auth.auth_bearer import JWTBearer
from app.auth.auth_handler import decode_jwt

TEST_SECRET = "test-secret-key-0123456789abcdef"


def test_decode_jwt_returns_payload_for_valid_token():
    token = jwt.encode(
        {"sub": "1", "is_superuser": True, "exp": int(time.time()) + 3600},
        TEST_SECRET,
        algorithm="HS256",
    )

    payload = decode_jwt(token)

    assert payload is not None
    assert payload["sub"] == "1"
    assert payload["is_superuser"] is True


def test_decode_jwt_raises_for_expired_token():
    token = jwt.encode(
        {"sub": "1", "is_superuser": True, "exp": int(time.time()) - 10},
        TEST_SECRET,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Token has expired"):
        decode_jwt(token)


def test_jwt_bearer_verify_jwt_rejects_non_superuser():
    token = jwt.encode(
        {"sub": "1", "is_superuser": False, "exp": int(time.time()) + 3600},
        TEST_SECRET,
        algorithm="HS256",
    )

    bearer = JWTBearer()
    assert bearer.verify_jwt(token) is False


def test_jwt_bearer_verify_jwt_accepts_superuser():
    token = jwt.encode(
        {"sub": "1", "is_superuser": True, "exp": int(time.time()) + 3600},
        TEST_SECRET,
        algorithm="HS256",
    )

    bearer = JWTBearer()
    assert bearer.verify_jwt(token) is True
