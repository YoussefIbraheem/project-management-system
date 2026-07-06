import pytest


def test_list_tasks_by_board(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id
    board_id = seeded_data["board"].id

    response = client.get(
        f"/api/v1/tasks/?project_id={project_id}&board_id={board_id}",
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
    from app.security.roles import MemberRole
    
    board = seeded_data["board"]
    column = seeded_data["doing"]
    project_id = seeded_data["project"].id
    member_role = seeded_data["member"].role

    response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers(),
        json={
            "title": "Created Task",
            "description": "Task body",
            "column_id": column.id,
            "priority": "medium",
            "board_id": board.id,
            "due_date": "2026-02-01T00:00:00Z",
        },
    )

    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 201
            payload = response.get_json()
            assert payload["title"] == "Created Task"
            assert payload["creator_id"] == "1"
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 201
            payload = response.get_json()
            assert payload["title"] == "Created Task"
            assert payload["creator_id"] == "1"
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
        case _:
            raise ValueError(f"Unknown role: {member_role}")


def test_create_task_rejects_missing_title(client, auth_headers, seeded_data):
    from app.security.roles import MemberRole
    
    member_role = seeded_data["member"].role
    
    # Only test with roles that can create tasks
    if member_role not in [MemberRole.OWNER.db_value, MemberRole.MANAGER.db_value]:
        pytest.skip("Test only applies to OWNER/MANAGER roles")
    
    response = client.post(
        "/api/v1/tasks/",
        headers=auth_headers(),
        json={"column_id": seeded_data["todo"].id, "board_id": seeded_data["board"].id},
    )

    assert response.status_code == 422


def test_update_task(client, auth_headers, seeded_data):
    from app.security.roles import MemberRole
    
    task_id = seeded_data["task"].id
    member_role = seeded_data["member"].role

    response = client.put(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers(),
        json={"title": "Updated Task", "priority": "high"},
    )

    # All members can update tasks
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["title"] == "Updated Task"
    assert payload["priority"] == "high"


def test_assign_task(client, auth_headers, seeded_data):
    from app.security.roles import MemberRole
    
    task_id = seeded_data["task"].id
    member_role = seeded_data["member"].role

    response = client.post(
        f"/api/v1/tasks/{task_id}/assign",
        headers=auth_headers(),
        json={"assignees_ids": ["1"]},
    )

    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 200
            assert response.get_json()["assignees"] == [{"user_id": "1"}]
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 200
            assert response.get_json()["assignees"] == [{"user_id": "1"}]
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
        case _:
            raise ValueError(f"Unknown role: {member_role}")


def test_unassign_task(client, auth_headers, seeded_data):
    from app.security.roles import MemberRole
    
    task_id = seeded_data["task"].id
    member_role = seeded_data["member"].role

    # First assign the task
    assign_response = client.post(
        f"/api/v1/tasks/{task_id}/assign",
        headers=auth_headers(),
        json={"assignees_ids": ["1"]},
    )

    # If assignment failed, skip unassign test for non-managers
    if member_role == MemberRole.MEMBER.db_value:
        assert assign_response.status_code == 403
        return

    assert assign_response.status_code == 200

    response = client.post(
        f"/api/v1/tasks/{task_id}/unassign",
        headers=auth_headers(),
        json={"assignees_ids": ["1"]},
    )

    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 200
            assert response.get_json()["assignees"] == []
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 200
            assert response.get_json()["assignees"] == []
        case _:
            raise ValueError(f"Unknown role: {member_role}")


def test_delete_task(client, auth_headers, seeded_data):
    from app.security.roles import MemberRole
    
    task_id = seeded_data["task"].id
    member_role = seeded_data["member"].role

    response = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers())

    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 200
            assert "deleted" in response.get_json()["message"]
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 200
            assert "deleted" in response.get_json()["message"]
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
        case _:
            raise ValueError(f"Unknown role: {member_role}")
