from datetime import datetime, timezone

from app.models import TaskPriority

from . import DummyModel, create_access_token


def _auth_headers(app, identity: str):
    with app.app_context():
        token = create_access_token(identity=identity)
    return {"Authorization": f"Bearer {token}"}


def test_tasks_list_returns_tasks(client, app, monkeypatch):
    expected = [
        {
            "id": 1,
            "title": "Task One",
            "description": "Task description",
            "column_id": 1,
            "priority": TaskPriority.MEDIUM.db_value,
            "creator_id": "1",
            "board_id": 21,
            "due_date": "2024-05-01T00:00:00",
            "created_at": "2024-05-01T00:00:00",
            "updated_at": None,
            "assignees": [{"user_id": "1"}],
        }
    ]

    def fake_get_tasks(
        board_id, creator_id, assigned_to, status, priority, limit, offset
    ):
        assert board_id == "21"
        assert creator_id == "1"
        assert assigned_to == "1"
        assert status is None
        assert priority == "medium"
        assert limit == "10"
        assert offset == "0"
        return [DummyModel(expected[0])]

    monkeypatch.setattr("app.apis.task_api.get_tasks", fake_get_tasks)

    headers = _auth_headers(app, "1")
    response = client.get(
        "/api/v1/tasks/?board_id=21&user_id=1&assigned_to=1&priority=medium&limit=10&offset=0",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == expected


def test_task_get_returns_task(client, app, monkeypatch):
    expected = {
        "id": 2,
        "title": "Task Two",
        "description": "Another task",
        "column_id": 2,
        "priority": TaskPriority.HIGH.db_value,
        "creator_id": "2",
        "board_id": 22,
        "due_date": "2024-06-01T00:00:00",
        "created_at": "2024-06-01T00:00:00",
        "updated_at": None,
        "assignees": [{"user_id": "2"}],
    }

    monkeypatch.setattr(
        "app.apis.task_api.get_task_by_id", lambda task_id: DummyModel(expected)
    )

    headers = _auth_headers(app, "2")
    response = client.get("/api/v1/tasks/2", headers=headers)

    assert response.status_code == 200
    assert response.get_json() == expected


def test_task_create_returns_task(client, app, monkeypatch):
    payload = {
        "title": "New Task",
        "description": "New task description",
        "column_id": 2,
        "priority": TaskPriority.LOW.db_value,
        "board_id": 23,
        "due_date": "2024-07-01T00:00:00",
    }
    expected = {
        "id": 3,
        "title": "New Task",
        "description": "New task description",
        "column_id": 2,
        "priority": TaskPriority.LOW.db_value,
        "creator_id": "3",
        "board_id": 23,
        "due_date": "2024-07-01T00:00:00",
        "created_at": "2024-07-01T00:00:00",
        "updated_at": None,
        "assignees": [],
    }

    def fake_create_task(task_data):
        assert task_data.creator_id == "3"
        assert task_data.title == "New Task"
        assert task_data.priority == TaskPriority.LOW.db_value
        return DummyModel(expected)

    monkeypatch.setattr("app.apis.task_api.create_task", fake_create_task)

    headers = _auth_headers(app, "3")
    response = client.post("/api/v1/tasks/", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.get_json() == expected


def test_task_update_returns_task(client, app, monkeypatch):
    expected = {
        "id": 4,
        "title": "Updated Task",
        "description": "Updated description",
        "column_id": 2,
        "priority": TaskPriority.HIGH.db_value,
        "creator_id": "4",
        "board_id": 24,
        "due_date": "2024-08-01T00:00:00",
        "created_at": "2024-08-01T00:00:00",
        "updated_at": "2024-08-02T00:00:00",
        "assignees": [],
    }

    monkeypatch.setattr(
        "app.apis.task_api.update_task", lambda task_id, task_data: DummyModel(expected)
    )

    headers = _auth_headers(app, "4")
    response = client.put(
        "/api/v1/tasks/4", json={"title": "Updated Task"}, headers=headers
    )

    assert response.status_code == 200
    assert response.get_json() == expected


def test_task_delete_returns_200(client, app, monkeypatch):
    monkeypatch.setattr("app.apis.task_api.delete_task", lambda task_id: True)

    response = client.delete("/api/v1/tasks/5", headers=_auth_headers(app, "5"))

    assert response.status_code == 200
    assert response.get_json() == {"message": "Task with id 5 has been deleted!"}


def test_task_update_no_data_returns_400(client, app):
    response = client.put("/api/v1/tasks/6", json={}, headers=_auth_headers(app, "6"))

    assert response.status_code == 400
    assert response.get_json() == {
        "error": {"status": 400, "message": "Request body is missing or not valid JSON"}
    }
