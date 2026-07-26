from datetime import datetime, timezone

from app.apis import email_log_api, notification_api, user_replica_api
from app.constants.task_event_types import TaskEventType
from app.main import app
from app.models.email_log import EmailStatus
from fastapi.testclient import TestClient


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_user_replica_routes_reject_missing_token():
    with TestClient(app) as client:
        response = client.get("/api/v1/users_replicas/")

    assert response.status_code == 401


def test_user_replica_routes_use_service_layer(monkeypatch, superuser_token):
    monkeypatch.setattr(
        user_replica_api,
        "list_users_replicas",
        lambda limit=100, offset=0: [
            {
                "user_id": "1",
                "email": "alice@example.com",
                "username": "alice",
                "display_name": "Alice",
            }
        ],
    )
    monkeypatch.setattr(
        user_replica_api,
        "get_user_replica_by_id",
        lambda user_id: {
            "user_id": user_id,
            "email": "alice@example.com",
            "username": "alice",
            "display_name": "Alice",
        },
    )

    with TestClient(app) as client:
        list_response = client.get(
            "/api/v1/users_replicas/", headers=_auth_headers(superuser_token)
        )
        detail_response = client.get(
            "/api/v1/users_replicas/1", headers=_auth_headers(superuser_token)
        )

    assert list_response.status_code == 200
    assert list_response.json()[0]["user_id"] == "1"
    assert detail_response.status_code == 200
    assert detail_response.json()["user_id"] == "1"


def test_notification_routes_use_service_layer(monkeypatch, superuser_token):
    monkeypatch.setattr(
        notification_api,
        "list_notifications",
        lambda limit=100, offset=0: [
            {
                "user_id": "1",
                "type": TaskEventType.TASK_CREATE,
                "subject": "task created",
                "body": "Task has been created successfully",
            }
        ],
    )

    monkeypatch.setattr(
        notification_api,
        "get_notification",
        lambda notification_id: {
            "user_id": "1",
            "type": TaskEventType.TASK_CREATE,
            "subject": "task created",
            "body": "Task has been created successfully",
        },
    )
    with TestClient(app) as client:
        list_response = client.get(
            "/api/v1/notifications/", headers=_auth_headers(superuser_token)
        )
        detail_response = client.get(
            "/api/v1/notifications/1", headers=_auth_headers(superuser_token)
        )

    assert list_response.status_code == 200
    assert list_response.json()[0]["user_id"] == "1"
    assert detail_response.status_code == 200
    assert detail_response.json()["user_id"] == "1"


def test_email_logs_use_service_layer(monkeypatch, superuser_token):
    monkeypatch.setattr(
        email_log_api,
        "list_email_logs",
        lambda limit=100, offset=0, notification_id=None: [
            {
                "id": "1",
                "email_address": "alice@example.com",
                "notification_id": 1,
                "recipient_email": "mack@example.com",
                "status": EmailStatus.PENDING,
                "attempts": 0,
                "error_message": None,
                "sent_at": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
            }
        ],
    )

    monkeypatch.setattr(
        email_log_api,
        "get_email_log",
        lambda email_log_id: {
            "id": "1",
            "email_address": "alice@example.com",
            "notification_id": 1,
            "recipient_email": "mack@example.com",
            "status": EmailStatus.PENDING,
            "attempts": 0,
            "error_message": None,
            "sent_at": datetime.now(timezone.utc),
            "created_at": datetime.now(timezone.utc),
        },
    )

    with TestClient(app) as client:
        list_response = client.get(
            "/api/v1/email-logs/",
            headers=_auth_headers(superuser_token),
        )
        detail_response = client.get(
            "/api/v1/email-logs/1", headers=_auth_headers(superuser_token)
        )

    assert list_response.status_code == 200
    assert list_response.json()[0]["notification_id"] == 1
    assert detail_response.status_code == 200
    assert detail_response.json()["notification_id"] == 1
