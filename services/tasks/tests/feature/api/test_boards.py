import pytest
from app.security.roles import MemberRole
from flask import abort
from shared.exceptions import APIException, ForbiddenException

from tests.conftest import logger


def test_list_boards_by_project(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id

    response = client.get(
        f"/api/v1/boards/?project_id={project_id}",
        headers=auth_headers(),
    )
    logger.info(response.get_json())
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

    member_role = seeded_data["member"].role
    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 201
            payload = response.get_json()
            assert payload["name"] == "Sprint Board"
            assert payload["project_id"] == project_id
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 201
            payload = response.get_json()
            assert payload["name"] == "Sprint Board"
            assert payload["project_id"] == project_id
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
        case _:
            raise ValueError(f"Unknown role: {member_role}")


def test_create_board_rejects_missing_project_id(client, auth_headers, seeded_data):
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

    member_role = seeded_data["member"].role
    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 200
            assert response.get_json()["name"] == "Renamed Board"
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 200
            assert response.get_json()["name"] == "Renamed Board"
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
        case _:
            raise ValueError(f"Unknown role: {member_role}")


def test_delete_board(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id

    response = client.delete(f"/api/v1/boards/{board_id}", headers=auth_headers())
    member_role = seeded_data["member"].role
    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 200
            assert "deleted successfully" in response.get_json()["message"]
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 200
            assert "deleted successfully" in response.get_json()["message"]
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
        case _:
            raise ValueError(f"Unknown role: {member_role}")


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


def test_create_board_column_rejects_schema_mismatch(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id
    response = client.post(
        f"/api/v1/boards/{board_id}/columns",
        headers=auth_headers(),
        json={
            "slug": "review",
            "label": "Review",
            "status_group": "unkown_group",
        },
    )

    assert response.status_code == 422


def test_delete_board_column(client, auth_headers, seeded_data):
    board_id = seeded_data["board"].id
    column_id = seeded_data["doing"].id
    member_role = seeded_data["member"].role
    response = client.delete(
        f"/api/v1/boards/{board_id}/columns/{column_id}",
        headers=auth_headers(),
    )
    match member_role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 204
        case MemberRole.MANAGER.db_value:
            assert response.status_code == 204
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
