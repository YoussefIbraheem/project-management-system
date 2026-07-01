
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
