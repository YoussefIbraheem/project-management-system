from . import DummyModel, app, auth_headers, client, create_access_token


def _auth_headers(app, identity: str):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


def test_projects_list_returns_projects(client, app, monkeypatch):
    expected = [
        {
            "id": 1,
            "name": "Test Project",
            "description": "Description",
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-01T00:00:00+00:00",
        }
    ]

    def fake_get_projects(limit, offset):
        assert limit == 5
        assert offset == 0
        return [DummyModel(expected[0])]

    monkeypatch.setattr("app.apis.project_api.get_projects", fake_get_projects)

    headers = _auth_headers(app, "10")
    response = client.get("/api/v1/projects/?limit=5&offset=0", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_details_returns_project(client, app, monkeypatch):
    expected = {
        "id": 2,
        "name": "Detail Project",
        "description": "Detail description",
        "created_at": "2024-01-02T00:00:00+00:00",
        "updated_at": "2024-01-02T00:00:00+00:00",
    }

    monkeypatch.setattr(
        "app.apis.project_api.get_project_by_id",
        lambda project_id: DummyModel(expected),
    )

    headers = _auth_headers(app, "20")
    response = client.get("/api/v1/projects/2", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_create_returns_201(client, app, monkeypatch):
    payload = {"name": "New Project", "description": "New description"}
    expected = {
        "id": 3,
        "name": "New Project",
        "description": "New description",
        "created_at": "2024-01-03T00:00:00+00:00",
        "updated_at": "2024-01-03T00:00:00+00:00",
    }

    monkeypatch.setattr(
        "app.apis.project_api.create_project",
        lambda project_data: DummyModel(expected),
    )

    headers = _auth_headers(app, "30")
    response = client.post("/api/v1/projects/", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.get_json() == expected


def test_project_update_returns_200(client, app, monkeypatch):
    expected = {
        "id": 4,
        "name": "Updated Project",
        "description": "Updated description",
        "created_at": "2024-01-04T00:00:00+00:00",
        "updated_at": "2024-01-05T00:00:00+00:00",
    }

    monkeypatch.setattr(
        "app.apis.project_api.update_project",
        lambda project_id, project_data: DummyModel(expected),
    )

    headers = _auth_headers(app, "40")
    response = client.put(
        "/api/v1/projects/4", json={"name": "Updated Project"}, headers=headers
    )

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_delete_returns_200(client, auth_headers, monkeypatch):
    monkeypatch.setattr("app.apis.project_api.delete_project", lambda project_id: True)

    response = client.delete("/api/v1/projects/5", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json() == {"message": "Project with id 5 has been deleted"}


def test_project_delete_not_found_returns_404(client, auth_headers, monkeypatch):
    from utils.exceptions import NotFoundException

    def fake_delete_project(project_id):
        raise NotFoundException(f"Project with id {project_id} does not exist")

    monkeypatch.setattr("app.apis.project_api.delete_project", fake_delete_project)

    response = client.delete("/api/v1/projects/5", headers=auth_headers())

    assert response.status_code == 404
    assert "error" in response.get_json()
    assert response.get_json()["error"]["status"] == 404
