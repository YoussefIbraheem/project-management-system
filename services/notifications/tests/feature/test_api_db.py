import pytest
from app.main import app
from app.services.email_log_service import create_email_log
from app.services.notification_service import create_notification
from app.services.user_replica_service import create_user_replica
from fastapi.testclient import TestClient


def _auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def seeded(engine):
    """A replica, a notification for it, and an email log for that."""
    replica = create_user_replica(
        user_id="1", username="alice", email="alice@example.com", display_name="Alice"
    )
    notification = create_notification(
        user_id="1",
        type="TASK_CREATE",
        subject="Task created",
        body="A task was created",
    )
    email_log = create_email_log(
        notification_id=notification.id,
        email_address="sender@example.com",
        recipient_email="alice@example.com",
        attempts=1,
    )
    return {"replica": replica, "notification": notification, "email_log": email_log}


def test_user_replica_list_returns_persisted_rows(seeded, superuser_token):
    with TestClient(app) as client:
        response = client.get("/api/v1/users_replicas/", headers=_auth(superuser_token))

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["user_id"] == "1"
    assert payload[0]["email"] == "alice@example.com"


def test_user_replica_detail_returns_the_row(seeded, superuser_token):
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/users_replicas/1", headers=_auth(superuser_token)
        )

    assert response.status_code == 200, response.text
    assert response.json()["username"] == "alice"


def test_user_replica_detail_returns_null_for_unknown_user(seeded, superuser_token):
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/users_replicas/does-not-exist", headers=_auth(superuser_token)
        )

    assert response.status_code == 200
    assert response.json() is None


def test_notification_list_returns_persisted_rows(seeded, superuser_token):
    with TestClient(app) as client:
        response = client.get("/api/v1/notifications/", headers=_auth(superuser_token))

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["type"] == "TASK_CREATE"
    assert payload[0]["user_id"] == "1"
    assert payload[0]["is_read"] is False


def test_notification_detail_returns_the_row(seeded, superuser_token):
    notification_id = seeded["notification"].id

    with TestClient(app) as client:
        response = client.get(
            f"/api/v1/notifications/{notification_id}", headers=_auth(superuser_token)
        )

    assert response.status_code == 200, response.text
    assert response.json()["id"] == notification_id


def test_notification_list_paginates(seeded, superuser_token):
    for i in range(3):
        create_notification(user_id="1", type="TASK_UPDATE", subject=f"s{i}", body="b")

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/notifications/",
            params={"limit": 2},
            headers=_auth(superuser_token),
        )

    assert response.status_code == 200, response.text
    assert len(response.json()) == 2


def test_email_log_list_returns_persisted_rows(seeded, superuser_token):
    with TestClient(app) as client:
        response = client.get("/api/v1/email-logs/", headers=_auth(superuser_token))

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["recipient_email"] == "alice@example.com"


def test_email_log_list_filters_by_notification(seeded, superuser_token):
    other = create_notification(
        user_id="1", type="TASK_UPDATE", subject="other", body="b"
    )
    create_email_log(
        notification_id=other.id,
        email_address="sender@example.com",
        recipient_email="alice@example.com",
        attempts=1,
    )

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/email-logs/",
            params={"notification_id": other.id},
            headers=_auth(superuser_token),
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["notification_id"] == other.id


def test_email_log_detail_returns_the_row(seeded, superuser_token):
    email_log_id = seeded["email_log"].id

    with TestClient(app) as client:
        response = client.get(
            f"/api/v1/email-logs/{email_log_id}", headers=_auth(superuser_token)
        )

    assert response.status_code == 200, response.text
    assert response.json()["id"] == email_log_id


def test_creating_a_notification_for_an_unknown_user_is_rejected(engine):
    """Notifications are keyed to a user replica; without one there is nobody
    to address the email to."""
    with pytest.raises(ValueError):
        create_notification(user_id="ghost", type="TASK_CREATE", subject="s", body="b")
