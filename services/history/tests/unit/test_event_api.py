from datetime import datetime, timezone
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.apis import event_api
from app.main import app


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_root_endpoint_requires_jwt_and_returns_project_name(superuser_token):
    with TestClient(app) as client:
        response = client.get("/", headers=_auth_headers(superuser_token))

    assert response.status_code == 200
    assert response.json() == {"project_name": "History Service"}


def test_root_endpoint_rejects_missing_token():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 403


def test_events_endpoint_returns_event_list(monkeypatch, superuser_token):
    events = [
        event_api.EventResponse(
            _id="1",
            actor_id="1",
            service="tasks",
            action="created",
            subject_id="1",
            subject_type="task",
            metadata={"key": "value"},
            timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
        )
    ]
    monkeypatch.setattr(event_api, "get_events", AsyncMock(return_value=events))

    with TestClient(app) as client:
        response = client.get("/events/", headers=_auth_headers(superuser_token))

    assert response.status_code == 200
    assert response.json()[0]["service"] == "tasks"


def test_events_endpoint_returns_event_by_id(monkeypatch, superuser_token):
    event = event_api.EventResponse(
        _id="1",
        actor_id="1",
        service="tasks",
        action="created",
        subject_id="1",
        subject_type="task",
        metadata={"key": "value"},
        timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    monkeypatch.setattr(event_api, "get_event_by_id", AsyncMock(return_value=event))

    with TestClient(app) as client:
        response = client.get("/events/1", headers=_auth_headers(superuser_token))

    assert response.status_code == 200
    assert response.json().get("_id", response.json().get("id")) == "1"


def test_events_endpoint_returns_404_for_missing_event(monkeypatch, superuser_token):
    monkeypatch.setattr(event_api, "get_event_by_id", AsyncMock(return_value=None))

    with TestClient(app) as client:
        response = client.get("/events/999", headers=_auth_headers(superuser_token))

    assert response.status_code == 404
    assert response.json()["detail"] == "Event not found"


def test_events_endpoint_rejects_non_superuser(regular_user_token):
    with TestClient(app) as client:
        response = client.get("/events/", headers=_auth_headers(regular_user_token))

    assert response.status_code == 403
