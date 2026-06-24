def test_list_boards_by_project(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id

    response = client.get(
        f"/api/v1/boards/?project_id={project_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert payload[0]["project_id"] == project_id
    assert {
        "id",
        "name",
        "description",
        "project_id",
        "columns",
        "created_at",
        "updated_at",
    } <= set(payload[0])


def test_get_board_details(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id

    response = client.get(f"/api/v1/boards/{board_id}", headers=auth_headers())

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == board_id
    assert payload["name"] == "Board 1"
    assert isinstance(payload["columns"], list)


def test_create_board_with_default_columns(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id

    response = client.post(
        "/api/v1/boards/",
        headers=auth_headers(),
        json={
            "name": "Sprint Board",
            "description": "Board",
            "project_id": project_id,
            "default_columns": True,
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["name"] == "Sprint Board"
    assert payload["project_id"] == project_id


def test_create_board_rejects_missing_project_id(client, auth_headers):
    response = client.post(
        "/api/v1/boards/",
        headers=auth_headers(),
        json={"name": "Broken Board"},
    )

    assert response.status_code == 422


def test_update_board(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id

    response = client.put(
        f"/api/v1/boards/{board_id}",
        headers=auth_headers(),
        json={"name": "Renamed Board"},
    )

    assert response.status_code == 200
    assert response.get_json()["name"] == "Renamed Board"


def test_delete_board(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id

    response = client.delete(f"/api/v1/boards/{board_id}", headers=auth_headers())

    assert response.status_code == 200
    assert "deleted successfully" in response.get_json()["message"]
