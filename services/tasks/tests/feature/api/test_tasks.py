def test_list_tasks_by_board(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id

    response = client.get(
        f"/api/v1/tasks/?board_id={board_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert payload[0]["board_id"] == board_id
    assert {
        "id",
        "title",
        "description",
        "priority",
        "column_id",
        "creator_id",
        "board_id",
        "due_date",
        "assignees",
        "created_at",
        "updated_at",
    } <= set(payload[0])


def test_get_task_details(client, auth_headers, seeded_data):
    task_id = seeded_data["task"].id

    response = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers())

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == task_id
    assert payload["title"] == "Task 1"
    assert payload["assignees"] == []


def test_create_task_validates_creator_and_returns_response(
    client, auth_headers, seeded_data
):
    board = seeded_data["board"]
    column = seeded_data["doing"]

    response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers("user-1"),
        json={
            "title": "Created Task",
            "description": "Task body",
            "column_id": column.id,
            "priority": "medium",
            "board_id": board.id,
            "due_date": "2026-02-01T00:00:00Z",
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["title"] == "Created Task"
    assert payload["creator_id"] == "user-1"


def test_create_task_rejects_missing_title(client, auth_headers, seeded_data):
    response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers(),
        json={"column_id": seeded_data["todo"].id, "board_id": seeded_data["board"].id},
    )

    assert response.status_code == 422


def test_update_task(client, auth_headers, seeded_data):
    task_id = seeded_data["task"].id

    response = client.put(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers(),
        json={"title": "Updated Task", "priority": "high"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["title"] == "Updated Task"
    assert payload["priority"] == "high"


def test_assign_task(client, auth_headers, seeded_data, db_session):
    response = client.post(
        f"/api/v1/tasks/{seeded_data['task'].id}/assign",
        headers=auth_headers(),
        json={"assignees_ids": ["1"]},
    )

    assert response.status_code == 200
    assert response.get_json()["assignees"] == [{"user_id": "1"}]


def test_unassign_task(client, auth_headers, seeded_data):
    task_id = seeded_data["task"].id
    client.post(
        f"/api/v1/tasks/{task_id}/assign",
        headers=auth_headers(),
        json={"assignees_ids": ["1"]},
    )

    response = client.post(
        f"/api/v1/tasks/{task_id}/unassign",
        headers=auth_headers(),
        json={"assignees_ids": ["1"]},
    )

    assert response.status_code == 200
    assert response.get_json()["assignees"] == []


def test_delete_task(client, auth_headers, seeded_data):
    task_id = seeded_data["task"].id

    response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers())

    assert response.status_code == 200
    assert "deleted" in response.get_json()["message"]
