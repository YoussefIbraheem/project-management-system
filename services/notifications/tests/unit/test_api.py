from fastapi.testclient import TestClient

from app.apis import user_replica_api
from app.main import app


def test_root_endpoint_returns_hello_world():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


def test_user_replica_routes_use_service_layer(monkeypatch):
    monkeypatch.setattr(
        user_replica_api,
        "list_users_replicas",
        lambda limit=100, offset=0: [  # noqa: ARG005
            {"user_id": "user-1", "email": "alice@example.com", "username": "alice", "display_name": "Alice"}
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
        list_response = client.get("/users_replicas/")
        detail_response = client.get("/users_replicas/user-1")

    assert list_response.status_code == 200
    assert list_response.json()[0]["user_id"] == "user-1"
    assert detail_response.status_code == 200
    assert detail_response.json()["user_id"] == "user-1"
