from utils.exceptions import NotFoundException
from . import DummyModel, create_access_token, client, app, auth_headers


def test_projects_list_returns_projects(client, app, monkeypatch):
    expected = [
        {
            "id": 1,
            "name": "Test Project",
            "description": "Description",
            "owner_id": 10,
        }
    ]

    def fake_get_projects_by_owner(owner_id, limit, offset):
        assert owner_id == "10"
        assert limit == "5"
        assert offset == "0"
        return [DummyModel(expected[0])]

    monkeypatch.setattr("app.apis.project_api.get_projects_by_owner", fake_get_projects_by_owner)

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='10')}"}

    response = client.get("/api/v1/projects/?owner_id=10&limit=5&offset=0", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_details_returns_project(client, app, monkeypatch):
    expected = {
        "id": 2,
        "name": "Detail Project",
        "description": "Detail description",
        "owner_id": 20,
    }

    monkeypatch.setattr(
        "app.apis.project_api.get_project_by_id",
        lambda project_id: DummyModel(expected),
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='20')}"}

    response = client.get("/api/v1/projects/2", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_project_create_returns_201(client, app, monkeypatch):
    payload = {"name": "New Project", "description": "New description"}
    expected = {
        "id": 3,
        "name": "New Project",
        "description": "New description",
        "owner_id": "30",
    }

    monkeypatch.setattr(
        "app.apis.project_api.create_project",
        lambda project_data: DummyModel(expected),
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='30')}"}

    response = client.post("/api/v1/projects/", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.get_json() == expected


def test_project_update_returns_200(client, app, monkeypatch):
    expected = {
        "id": 4,
        "name": "Updated Project",
        "description": "Updated description",
        "owner_id": 40,
    }

    monkeypatch.setattr(
        "app.apis.project_api.update_project",
        lambda project_id, project_data: DummyModel(expected),
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='40')}"}

    response = client.put("/api/v1/projects/4", json={"name": "Updated Project"}, headers=headers)

    assert response.status_code == 200  # was 201
    assert response.get_json() == expected


def test_project_delete_returns_200(client, auth_headers, monkeypatch):
    monkeypatch.setattr("app.apis.project_api.delete_project", lambda project_id: True)

    response = client.delete("/api/v1/projects/5", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {"message": "Project deleted successfully"}


def test_project_delete_not_found_returns_404(client, auth_headers, monkeypatch):
    def fake_delete_project(project_id):
        raise NotFoundException(f"Project with id {project_id} does not exist")

    monkeypatch.setattr("app.apis.project_api.delete_project", fake_delete_project)

    response = client.delete("/api/v1/projects/5", headers=auth_headers)

    assert response.status_code == 404
    assert "error" in response.get_json()
    assert response.get_json()["error"]["status"] == 404