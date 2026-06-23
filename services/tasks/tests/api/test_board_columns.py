def test_list_board_columns(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id

    response = client.get(f"/api/v1/boards/{board_id}/columns", headers=auth_headers())

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert len(payload) == 2
    assert {"id", "board_id", "slug", "label", "status_group"} <= set(payload[0])


def test_get_board_column(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id
    column_id = seeded_data["todo"].id

    response = client.get(
        f"/api/v1/boards/{board_id}/columns/{column_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == column_id
    assert payload["board_id"] == board_id
    assert payload["slug"] == "todo"


import pytest


def test_create_board_column_rejects_schema_mismatch(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id

    with pytest.raises(Exception, match="Transaction Failed"):
        client.post(
            f"/api/v1/boards/{board_id}/columns",
            headers=auth_headers(),
            json={"slug": "review", "label": "Review", "status_group": "done"},
        )


def test_delete_board_column(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id
    column_id = seeded_data["doing"].id

    response = client.delete(
        f"/api/v1/boards/{board_id}/columns/{column_id}",
        headers=auth_headers(),
    )

    assert response.status_code == 204
