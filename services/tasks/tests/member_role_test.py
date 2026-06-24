from utils.exceptions import BadRequestException, NotFoundException

from . import DummyModel, app, auth_headers, client, create_access_token


def _auth_headers(app, identity: str = "10"):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


def test_roles_list_returns_roles(client, app, monkeypatch):
    expected = [
        {
            "id": 1,
            "label": "Admin",
            "slug": "admin",
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
        },
        {
            "id": 2,
            "label": "Member",
            "slug": "member",
            "created_at": "2024-01-02T00:00:00+00:00",
            "updated_at": "2024-01-02T00:00:00+00:00",
        },
    ]

    monkeypatch.setattr(
        "app.apis.member_role_api.get_roles",
        lambda: [DummyModel(expected[0]), DummyModel(expected[1])],
    )

    response = client.get("/api/v1/roles/", headers=_auth_headers(app))

    assert response.status_code == 200
    assert response.get_json() == expected


def test_role_get_returns_role(client, app, monkeypatch):
    expected = {
        "id": 1,
        "label": "Admin",
        "slug": "admin",
        "created_at": "2024-01-01T00:00:00+00:00",
        "updated_at": "2024-01-01T00:00:00+00:00",
    }

    monkeypatch.setattr(
        "app.apis.member_role_api.get_role",
        lambda role_id: DummyModel(expected),
    )

    response = client.get("/api/v1/roles/1", headers=_auth_headers(app))

    assert response.status_code == 200
    assert response.get_json() == expected


def test_role_create_returns_201_and_slugifies(client, app, monkeypatch):
    payload = {"label": "Project Owner", "slug": "Project Owner"}
    expected = {
        "id": 3,
        "label": "Project Owner",
        "slug": "project-owner",
        "created_at": "2024-01-03T00:00:00+00:00",
        "updated_at": "2024-01-03T00:00:00+00:00",
    }

    def fake_create_role(role_data):
        assert role_data.label == "Project Owner"
        assert role_data.slug == "Project Owner"
        return DummyModel(expected)

    monkeypatch.setattr("app.apis.member_role_api.create_role", fake_create_role)

    response = client.post("/api/v1/roles/", json=payload, headers=_auth_headers(app))

    assert response.status_code == 201
    assert response.get_json() == expected


def test_role_create_rejects_missing_body(client, app):
    response = client.post("/api/v1/roles/", headers=_auth_headers(app), json={})

    assert response.status_code == 400
    assert (
        response.get_json()["error"]["message"]
        == "Request body is missing or not valid JSON"
    )


def test_role_create_rejects_missing_fields(client, app):
    response = client.post(
        "/api/v1/roles/",
        json={"label": "No slug"},
        headers=_auth_headers(app),
    )

    assert response.status_code == 422
    assert response.get_json()["error"]["status"] == 422


def test_role_create_rejects_duplicate_slug(client, app, monkeypatch):
    from utils.exceptions import BadRequestException

    def fake_create_role(role_data):
        raise BadRequestException("Role slug 'admin' is already taken")

    monkeypatch.setattr("app.apis.member_role_api.create_role", fake_create_role)

    response = client.post(
        "/api/v1/roles/",
        json={"label": "Admin", "slug": "admin"},
        headers=_auth_headers(app),
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["status"] == 400


def test_role_update_returns_200(client, app, monkeypatch):
    payload = {"label": "Owner", "slug": "Owner"}
    expected = {
        "id": 1,
        "label": "Owner",
        "slug": "owner",
        "created_at": "2024-01-01T00:00:00+00:00",
        "updated_at": "2024-01-04T00:00:00+00:00",
    }

    def fake_update_role(role_id, role_data):
        assert role_id == 1
        assert role_data.label == "Owner"
        assert role_data.slug == "Owner"
        return DummyModel(expected)

    monkeypatch.setattr("app.apis.member_role_api.update_role", fake_update_role)

    response = client.put("/api/v1/roles/1", json=payload, headers=_auth_headers(app))

    assert response.status_code == 200
    assert response.get_json() == expected


def test_role_update_rejects_missing_body(client, app):
    response = client.put("/api/v1/roles/1", headers=_auth_headers(app), json={})

    assert response.status_code == 400
    assert (
        response.get_json()["error"]["message"]
        == "Request body is missing or not valid JSON"
    )


def test_role_update_rejects_invalid_payload(client, app):
    response = client.put(
        "/api/v1/roles/1",
        json={"slug": "only-slug"},
        headers=_auth_headers(app),
    )

    assert response.status_code == 422


def test_role_get_returns_404_when_missing(client, app, monkeypatch):
    def fake_get_role(role_id):
        raise NotFoundException(f"Role with id {role_id} does not exist")

    monkeypatch.setattr("app.apis.member_role_api.get_role", fake_get_role)

    response = client.get("/api/v1/roles/999", headers=_auth_headers(app))

    assert response.status_code == 404
    assert response.get_json()["error"]["status"] == 404


def test_role_delete_returns_200(client, app, monkeypatch):
    monkeypatch.setattr("app.apis.member_role_api.delete_role", lambda role_id: True)

    response = client.delete("/api/v1/roles/1", headers=_auth_headers(app))

    assert response.status_code == 200
    assert response.get_json() == {"message": "Role deleted successfully"}


def test_role_delete_returns_404_when_missing(client, app, monkeypatch):
    def fake_delete_role(role_id):
        raise NotFoundException(f"Role with id {role_id} does not exist")

    monkeypatch.setattr("app.apis.member_role_api.delete_role", fake_delete_role)

    response = client.delete("/api/v1/roles/999", headers=_auth_headers(app))

    assert response.status_code == 404
    assert response.get_json()["error"]["status"] == 404
