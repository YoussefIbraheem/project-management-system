import os
import subprocess
import time
import uuid
from pathlib import Path

import httpx
import jwt
import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

USERS_URL = os.getenv("PMS_USERS_URL", "http://localhost:8000")
TASKS_URL = os.getenv("PMS_TASKS_URL", "http://localhost:8080")
HISTORY_URL = os.getenv("PMS_HISTORY_URL", "http://localhost:5006")
NOTIFICATIONS_URL = os.getenv("PMS_NOTIFICATIONS_URL", "http://localhost:8081")

JWT_SECRET_KEY = os.getenv(
    "PMS_JWT_SECRET_KEY",
    "mh/DifmKQnnLkCfZALrX5wzYhcS7npjE33cBTGU/kHZyDjtnt7zvBf+jVH9TglmftG+UoqA4TuuuX/+40sOwXA==",
)
JWT_ALGORITHM = "HS256"


POLL_TIMEOUT = float(os.getenv("PMS_POLL_TIMEOUT", "20"))
POLL_INTERVAL = 0.5


def mint_token(user_id: str, *, is_superuser: bool) -> str:
    return jwt.encode(
        {
            "sub": str(user_id),
            "user_id": str(user_id),
            "is_superuser": is_superuser,
            "exp": int(time.time()) + 3600,
        },
        JWT_SECRET_KEY,
        algorithm=JWT_ALGORITHM,
    )


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def eventually(probe, *, timeout: float = POLL_TIMEOUT, describe: str = "condition"):
    """Poll `probe` until it returns something truthy, then return it."""
    deadline = time.monotonic() + timeout
    last_error = None
    while time.monotonic() < deadline:
        try:
            result = probe()
        except Exception as exc:
            last_error = exc
        else:
            if result:
                return result
        time.sleep(POLL_INTERVAL)
    pytest.fail(
        f"Timed out after {timeout}s waiting for {describe} (last error: {last_error})"
    )


@pytest.fixture(scope="session")
def http():
    with httpx.Client(timeout=10.0) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def require_stack(http):
    """Fail fast with a clear message when the compose stack isn't up."""
    for name, url in (
        ("users", f"{USERS_URL}/health/"),
        ("tasks", TASKS_URL),
        ("history", HISTORY_URL),
        ("notifications", NOTIFICATIONS_URL),
    ):
        try:
            http.get(url)
        except httpx.HTTPError as exc:
            pytest.exit(
                f"{name} service unreachable at {url}: {exc}. "
                "Start the stack first: docker compose up -d --wait",
                returncode=1,
            )


@pytest.fixture(scope="session")
def reader_token():
    """History and notifications read APIs require a superuser JWT.

    Those services verify tokens with plain PyJWT, so a self-minted HS256
    token signed with the shared secret is accepted. The users service uses
    simplejwt, which enforces its own claim structure — see `admin_token`.
    """
    return mint_token("integration-reader", is_superuser=True)


ADMIN_EMAIL = "itest-admin@example.com"
ADMIN_PASSWORD = "ItestAdmin123"


@pytest.fixture(scope="session", autouse=True)
def admin_account():
    """Bootstrap a superuser in the users service.

    There is no public endpoint that can grant superuser, so this is done
    out-of-band. It is idempotent, so reruns reuse the same account.
    """
    script = (
        "from accounts.models import User;"
        f"u,_=User.objects.get_or_create(email='{ADMIN_EMAIL}',"
        "defaults={'username':'itest_admin'});"
        "u.is_superuser=True;u.is_staff=True;u.is_verified=True;u.is_active=True;"
        f"u.set_password('{ADMIN_PASSWORD}');u.save();print('ready')"
    )
    result = subprocess.run(
        [
            "docker",
            "compose",
            "exec",
            "-T",
            "users-service",
            "python",
            "manage.py",
            "shell",
            "-c",
            script,
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False
    )
    if "ready" not in result.stdout:
        pytest.exit(
            f"Could not bootstrap the integration admin account:\n{result.stdout}\n{result.stderr}",
            returncode=1,
        )


@pytest.fixture()
def admin_token(http):
    """A genuine simplejwt access token, required for users-service calls.

    Access tokens live for 2 minutes, so this is deliberately function-scoped
    rather than cached for the session.
    """
    response = http.post(
        f"{USERS_URL}/api/v1/login/",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 201, response.text
    return response.json()["tokens"]["access"]


@pytest.fixture()
def registered_user(http, admin_token):
    """Register a real user through the users service, returning its identity.

    Registration is itself the event producer under test, so this fixture is
    deliberately a real HTTP call rather than a DB insert.
    """
    suffix = uuid.uuid4().hex[:10]
    payload = {
        "email": f"itest_{suffix}@example.com",
        "username": f"itest_{suffix}",
        "password": "IntegPass123",
        "password_confirm": "IntegPass123",
        "first_name": "Integration",
        "last_name": "Test",
    }

    response = http.post(f"{USERS_URL}/api/v1/register/", json=payload)
    assert response.status_code == 201, response.text

    listing = http.get(
        f"{USERS_URL}/api/v1/users/",
        params={"email": payload["email"]},
        headers=auth(admin_token),
    )
    assert listing.status_code == 200, listing.text
    assert listing.json(), f"registered user {payload['email']} not found in user list"

    return {**payload, "id": str(listing.json()[0]["id"])}


@pytest.fixture()
def history_events(http, reader_token):
    def _fetch(**params):
        response = http.get(
            f"{HISTORY_URL}/api/v1/events/",
            params=params,
            headers=auth(reader_token),
        )
        assert response.status_code == 200, response.text
        return response.json()

    return _fetch
