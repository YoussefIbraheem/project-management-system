import pytest
from app.models import Project
from app.security.roles import MemberRole

from tests.conftest import logger


def test_list_projects_returns_projects(client, auth_headers, db_session, seeded_data):
    extra = Project(name="Beta", description="Second project")
    db_session.add(extra)
    db_session.commit()

    response = client.get("/api/v1/projects/", headers=auth_headers())

    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert len(payload) >= 2
    first = payload[0]
    assert {"id", "name", "description", "created_at", "updated_at"} <= set(first)


def test_get_project_details(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id

    response = client.get(f"/api/v1/projects/{project_id}", headers=auth_headers())

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["id"] == project_id
    assert payload["name"] == "Alpha"


def test_create_project_validates_and_creates(client, auth_headers):
    response = client.post(
        "/api/v1/projects/",
        headers=auth_headers(),
        json={"name": "New Project", "description": "Created by test"},
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["name"] == "New Project"
    assert payload["description"] == "Created by test"
    assert payload["id"] is not None


def test_create_project_rejects_missing_name(client, auth_headers):
    response = client.post(
        "/api/v1/projects/",
        headers=auth_headers(),
        json={"description": "Missing name"},
    )

    assert response.status_code == 422
    payload = response.get_json()
    assert payload["error"]["status"] == 422
    assert payload["error"]["message"] == "Validation Error"


def test_update_project(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id
    response = client.put(
        f"/api/v1/projects/{project_id}",
        headers=auth_headers(),
        json={"name": "Renamed Project"},
    )
    role = seeded_data["member"].role

    match role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 200
            payload = response.get_json()
            assert payload["name"] == "Renamed Project"
            logger.info(f"PAYLOAD: {payload}")

        case MemberRole.MANAGER.db_value:
            assert response.status_code == 200
            payload = response.get_json()
            assert payload["name"] == "Renamed Project"
            logger.info(f"PAYLOAD: {payload}")
        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
            payload = response.get_json()
            assert payload["error"]["status"] == 403
            logger.info(f"PAYLOAD: {payload}")

        case _:
            raise ValueError("Invalid role value")


# def test_delete_project_surfaces_integrity_issue(client, auth_headers, seeded_data):
#     project_id = seeded_data["project"].id

#     with pytest.raises(Exception, match="Transaction Failed"):
#         response = client.delete(
#             f"/api/v1/projects/{project_id}", headers=auth_headers()
#         )
#         logger.info(f"RESPONSE DATA:{response.get_json()}")


def test_delete_project(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id
    response = client.delete(f"/api/v1/projects/{project_id}", headers=auth_headers())
    role = seeded_data["member"].role

    match role:
        case MemberRole.OWNER.db_value:
            assert response.status_code == 200
            logger.info("Project deleted successfully")

        case MemberRole.MANAGER.db_value:
            assert response.status_code == 403
            payload = response.get_json()
            assert payload["error"]["status"] == 403
            logger.info(f"PAYLOAD: {payload}")

        case MemberRole.MEMBER.db_value:
            assert response.status_code == 403
            payload = response.get_json()
            assert payload["error"]["status"] == 403
            logger.info(f"PAYLOAD: {payload}")

        case _:
            raise ValueError("Invalid role value")

def test_get_project_member_details_returns_404_for_string_user_id(
    client, auth_headers, seeded_data
):
    project_id = seeded_data["project"].id

    response = client.get(
        f"/api/v1/projects/{project_id}/members/user-1",
        headers=auth_headers(),
    )

    assert response.status_code == 404


def test_create_project_member_missing_user_id(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id
    headers = auth_headers(is_superuser=True)
    response = client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=headers,
        data="",
        content_type="application/json",
    )

    assert response.status_code == 400


def test_create_project_member_missing_role_id(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id

    response = client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=auth_headers(),
        json={"user_id": "user-1"},
    )

    assert response.status_code == 422


def test_create_project_member_missing_body(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id

    response = client.post(
        f"/api/v1/projects/{project_id}/members",
        headers=auth_headers(),
        data="",
        content_type="application/json",
    )

    assert response.status_code == 400


def test_update_project_member_role(client, auth_headers, seeded_data):
    project_id = seeded_data["project"].id
    new_role_id = 2

    response = client.put(
        f"/api/v1/projects/{project_id}/members/user-1",
        headers=auth_headers(),
        json={"role_id": new_role_id},
    )

    assert response.status_code == 404


def test_delete_project_member_returns_404_for_string_user_id(
    client, auth_headers, seeded_data
):
    project_id = seeded_data["project"].id

    response = client.delete(
        f"/api/v1/projects/{project_id}/members/user-1",
        headers=auth_headers(),
    )

    assert response.status_code == 404
