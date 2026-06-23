"""Test cases for project member API endpoints."""

from utils.exceptions import BadRequestException, NotFoundException

from . import DummyModel, app, auth_headers, client, create_access_token


def test_project_members_list_returns_members(client, app, monkeypatch):
    """Test GET /projects/<project_id>/members returns list of members."""
    expected = [
        {
            "id": 1,
            "project_id": 1,
            "user_id": "user1",
            "role_id": 1,
        },
        {
            "id": 2,
            "project_id": 1,
            "user_id": "user2",
            "role_id": 2,
        },
    ]

    def fake_get_members(project_id):
        assert project_id == 1
        return expected

    monkeypatch.setattr("app.apis.project_member_api.get_members", fake_get_members)

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='10')}"}

    response = client.get("/api/v1/projects/1/members", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_members_list_empty_returns_empty_list(client, app, monkeypatch):
    """Test GET /projects/<project_id>/members returns empty list when no members exist."""
    monkeypatch.setattr(
        "app.apis.project_member_api.get_members", lambda project_id: []
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='10')}"}
        response = client.get("/api/v1/projects/1/members", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == []


def test_project_members_list_project_not_found_returns_404(
    client, auth_headers, monkeypatch
):
    """Test GET /projects/<project_id>/members returns 404 when project doesn't exist."""

    def fake_get_members(project_id):
        raise NotFoundException(f"Project with id {project_id} does not exist")

    monkeypatch.setattr("app.apis.project_member_api.get_members", fake_get_members)

    response = client.get("/api/v1/projects/999/members", headers=auth_headers())

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_project_member_details_returns_member(client, app, monkeypatch):
    """Test GET /projects/<project_id>/members/<user_id> returns member details."""
    expected = {
        "id": 1,
        "project_id": 1,
        "user_id": 1,
        "role_id": 1,
    }

    def fake_get_member(project_id, user_id):
        assert project_id == 1
        assert user_id == 1
        return expected

    monkeypatch.setattr("app.apis.project_member_api.get_member", fake_get_member)

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='10')}"}
        response = client.get("/api/v1/projects/1/members/1", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_member_details_user_not_in_project_returns_404(
    client, auth_headers, monkeypatch
):
    """Test GET /projects/<project_id>/members/<user_id> returns 404 when user not in project."""

    def fake_get_member(project_id, user_id):
        raise NotFoundException(
            f"User with id {user_id} does not exist in project with id {project_id}"
        )

    monkeypatch.setattr("app.apis.project_member_api.get_member", fake_get_member)

    response = client.get("/api/v1/projects/1/members/999", headers=auth_headers())

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_project_member_create_returns_201(client, app, monkeypatch):
    """Test POST /projects/<project_id>/members creates new member."""
    payload = {
        "user_id": "newuser",
        "role_id": 2,
    }
    expected = {
        "id": 3,
        "project_id": 1,
        "user_id": "newuser",
        "role_id": 2,
    }

    def fake_create_member(project_id, member_data):
        assert project_id == 1
        assert member_data.user_id == "newuser"
        assert member_data.role_id == 2
        return expected

    monkeypatch.setattr("app.apis.project_member_api.create_member", fake_create_member)

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='10')}"}
        response = client.post(
            "/api/v1/projects/1/members", json=payload, headers=headers
        )

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_member_create_missing_body_returns_400(
    client, auth_headers, monkeypatch
):
    """Test POST /projects/<project_id>/members returns error when body is missing."""
    response = client.post("/api/v1/projects/1/members", headers=auth_headers())

    assert response.status_code == 415  # Unsupported Media Type


def test_project_member_create_invalid_json_returns_400(client, auth_headers):
    """Test POST /projects/<project_id>/members returns error when JSON is invalid."""
    response = client.post(
        "/api/v1/projects/1/members",
        data="invalid json",
        content_type="application/json",
        headers=auth_headers(),
    )

    assert response.status_code == 400


def test_project_member_create_project_not_found_returns_404(
    client, auth_headers, monkeypatch
):
    """Test POST /projects/<project_id>/members returns 404 when project doesn't exist."""
    payload = {
        "user_id": "newuser",
        "role_id": 2,
    }

    def fake_create_member(project_id, member_data):
        raise NotFoundException(f"Project with id {project_id} does not exist")

    monkeypatch.setattr("app.apis.project_member_api.create_member", fake_create_member)

    response = client.post(
        "/api/v1/projects/999/members", json=payload, headers=auth_headers()
    )

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_project_member_update_role_returns_200(client, app, monkeypatch):
    """Test PUT /projects/<project_id>/members/<user_id> updates member role."""
    payload = {
        "role_id": 3,
    }
    expected = {
        "id": 1,
        "project_id": 1,
        "user_id": "user1",
        "role_id": 3,
    }

    def fake_update_member_role(project_id, user_id, role_id):
        assert project_id == 1
        assert user_id == 1
        assert role_id == 3
        return expected

    monkeypatch.setattr(
        "app.apis.project_member_api.update_member_role",
        fake_update_member_role,
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='10')}"}
        response = client.put(
            "/api/v1/projects/1/members/1", json=payload, headers=headers
        )

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_member_update_role_missing_role_id_returns_400(client, auth_headers):
    """Test PUT /projects/<project_id>/members/<user_id> returns error when role_id is missing."""
    payload = {}
    response = client.put(
        "/api/v1/projects/1/members/1", json=payload, headers=auth_headers()
    )

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_project_member_update_role_missing_body_returns_400(client, auth_headers):
    """Test PUT /projects/<project_id>/members/<user_id> returns error when body is missing."""
    response = client.put("/api/v1/projects/1/members/1", headers=auth_headers())

    assert response.status_code == 415  # Unsupported Media Type


def test_project_member_update_role_member_not_found_returns_404(
    client, auth_headers, monkeypatch
):
    """Test PUT /projects/<project_id>/members/<user_id> returns 404 when member doesn't exist."""
    payload = {
        "role_id": 3,
    }

    def fake_update_member_role(project_id, user_id, role_id):
        raise NotFoundException(
            f"User with id {user_id} does not exist in project with id {project_id}"
        )

    monkeypatch.setattr(
        "app.apis.project_member_api.update_member_role",
        fake_update_member_role,
    )

    response = client.put(
        "/api/v1/projects/1/members/999", json=payload, headers=auth_headers()
    )

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_project_member_update_role_invalid_role_returns_404(
    client, auth_headers, monkeypatch
):
    """Test PUT /projects/<project_id>/members/<user_id> returns 404 when role doesn't exist."""
    payload = {
        "role_id": 999,
    }

    def fake_update_member_role(project_id, user_id, role_id):
        raise NotFoundException(f"Role with id {role_id} does not exist")

    monkeypatch.setattr(
        "app.apis.project_member_api.update_member_role",
        fake_update_member_role,
    )

    response = client.put(
        "/api/v1/projects/1/members/1", json=payload, headers=auth_headers()
    )

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_project_member_delete_returns_200(client, auth_headers, monkeypatch):
    """Test DELETE /projects/<project_id>/members/<user_id> deletes member."""
    monkeypatch.setattr(
        "app.apis.project_member_api.delete_member", lambda project_id, user_id: True
    )

    response = client.delete("/api/v1/projects/1/members/1", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json() == {"message": "Member deleted successfully"}


def test_project_member_delete_member_not_found_returns_404(
    client, auth_headers, monkeypatch
):
    """Test DELETE /projects/<project_id>/members/<user_id> returns 404 when member doesn't exist."""

    def fake_delete_member(project_id, user_id):
        raise NotFoundException(
            f"User with id {user_id} does not exist in project with id {project_id}"
        )

    monkeypatch.setattr("app.apis.project_member_api.delete_member", fake_delete_member)

    response = client.delete("/api/v1/projects/1/members/999", headers=auth_headers())

    assert response.status_code == 404
    assert "error" in response.get_json()


def test_project_member_delete_project_not_found_returns_404(
    client, auth_headers, monkeypatch
):
    """Test DELETE /projects/<project_id>/members/<user_id> returns 404 when project doesn't exist."""

    def fake_delete_member(project_id, user_id):
        raise NotFoundException(f"Project with id {project_id} does not exist")

    monkeypatch.setattr("app.apis.project_member_api.delete_member", fake_delete_member)

    response = client.delete("/api/v1/projects/999/members/1", headers=auth_headers())

    assert response.status_code == 404
    assert "error" in response.get_json()
