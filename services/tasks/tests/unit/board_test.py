from shared.exceptions import NotFoundException

from . import DummyModel, app, auth_headers, client, create_access_token


def test_boards_get_returns_boards(client, app, monkeypatch):

    expected = [
        {
            "id": 1,
            "name": "Board 1",
            "description": "Board description",
            "project_id": 11,
            "columns": ["ToDO", "InProgress", "Done"],
        }
    ]

    def fake_get_board_by_project(project_id, limit, offset):
        assert project_id == "11"
        assert limit == "2"
        assert offset == "0"
        return [DummyModel(expected[0])]

    monkeypatch.setattr(
        "app.apis.board_api.get_board_by_project", fake_get_board_by_project
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='11')}"}

    response = client.get(
        "/api/v1/boards/?project_id=11&limit=2&offset=0", headers=headers
    )

    assert response.status_code == 200
    assert response.get_json() == expected


def test_board_get_returns_board(client, app, monkeypatch):
    expected = {
        "id": 2,
        "name": "Board 2",
        "description": "More details",
        "project_id": 12,
        "columns": ["ToDO", "InProgress", "Done"],
        "created_at": "2024-02-01T00:00:00",
        "updated_at": None,
    }

    monkeypatch.setattr(
        "app.apis.board_api.get_board_by_id", lambda board_id: DummyModel(expected)
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='12')}"}

    response = client.get("/api/v1/boards/2", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_board_create_returns_created_board(client, app, monkeypatch):
    payload = {
        "name": "New Board",
        "description": "Board test",
        "project_id": 13,
        "columns": ["ToDO", "InProgress", "Done"],
    }
    expected = {
        "id": 3,
        "name": "New Board",
        "description": "Board test",
        "project_id": 13,
        "columns": ["ToDO", "InProgress", "Done"],
        "created_at": "2024-03-01T00:00:00",
        "updated_at": None,
    }

    monkeypatch.setattr(
        "app.apis.board_api.create_board", lambda board_data: DummyModel(expected)
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='13')}"}

    response = client.post("/api/v1/boards/", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.get_json() == expected


def test_board_update_returns_updated_board(client, app, monkeypatch):
    expected = {
        "id": 4,
        "name": "Updated Board",
        "description": "Updated description",
        "project_id": 14,
        "columns": ["ToDO", "InProgress", "Done"],
        "created_at": "2024-04-01T00:00:00",
        "updated_at": "2024-04-02T00:00:00",
    }

    monkeypatch.setattr(
        "app.apis.board_api.update_board",
        lambda board_id, board_data: DummyModel(expected),
    )

    with app.app_context():
        headers = {"Authorization": f"Bearer {create_access_token(identity='14')}"}

    response = client.put(
        "/api/v1/boards/4", json={"name": "Updated Board"}, headers=headers
    )

    assert response.status_code == 200
    assert response.get_json() == expected


def test_board_delete_returns_200(client, auth_headers, monkeypatch):
    monkeypatch.setattr("app.apis.board_api.delete_board", lambda board_id: True)

    response = client.delete("/api/v1/boards/5", headers=auth_headers())

    assert response.status_code == 200
    assert response.get_json() == {"message": "Board with id 5 deleted successfully"}


def test_board_delete_not_found_returns_404(client, auth_headers, monkeypatch):
    def fake_delete_board(board_id):
        assert board_id == 5  # board_id is an int, not a string
        return False

    monkeypatch.setattr("app.apis.board_api.delete_board", fake_delete_board)

    response = client.delete("/api/v1/boards/5", headers=auth_headers())

    assert response.status_code == 404
    assert "error" in response.get_json()
