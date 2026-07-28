import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock

import jwt
import pytest

SERVICE_ROOT = Path(__file__).resolve().parents[1]
if str(SERVICE_ROOT) not in sys.path:
    sys.path.insert(0, str(SERVICE_ROOT))


from app import main as history_main

TEST_SECRET = "test-secret-key-0123456789abcdef"


@pytest.fixture(autouse=True)
def patch_history_settings(monkeypatch):
    monkeypatch.setattr(history_main.settings, "JWT_SECRET_KEY", TEST_SECRET)
    monkeypatch.setattr(history_main.settings, "ALGORITHM", "HS256")
    monkeypatch.setattr(history_main, "connect_db", AsyncMock(return_value=None))
    monkeypatch.setattr(history_main, "close_db", AsyncMock(return_value=None))
    yield


@pytest.fixture()
def superuser_token():
    payload = {
        "sub": "1",
        "is_superuser": True,
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")


@pytest.fixture()
def regular_user_token():
    payload = {
        "sub": "1",
        "is_superuser": False,
        "exp": int(time.time()) + 3600,
    }
    return jwt.encode(payload, TEST_SECRET, algorithm="HS256")
