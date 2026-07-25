from app.apis import user_replica_api
from app.main import app
from fastapi.testclient import TestClient


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_user_replica_routes_reject_missing_token():
    with TestClient(app) as client:
        response = client.get(
            "/api/v1/users_replicas/"
        )

    assert response.status_code == 401


def test_user_replica_routes_use_service_layer(monkeypatch, superuser_token):
    monkeypatch.setattr(
        user_replica_api,
        "list_users_replicas",
        lambda limit=100, offset=0: [  # noqa: ARG005
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
        lambda user_id: {  # noqa: ARG005
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
