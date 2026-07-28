import pytest
from conftest import NOTIFICATIONS_URL, TASKS_URL, auth, eventually, mint_token

pytestmark = pytest.mark.smtp


@pytest.fixture()
def member_added(http, registered_user):
    """Owner creates a project, then adds a second registered user to it."""
    owner_token = mint_token(registered_user["id"], is_superuser=True)

    created = http.post(
        f"{TASKS_URL}/api/v1/projects/",
        headers=auth(owner_token),
        json={"name": "Notify Project", "description": "member-add notification test"},
    )
    assert created.status_code == 201, created.text
    project = created.json()

    member_id = registered_user["id"]
    response = http.post(
        f"{TASKS_URL}/api/v1/projects/{project['id']}/members",
        headers=auth(owner_token),
        json={"user_id": member_id, "role": "MEMBER"},
    )
    assert response.status_code == 201, response.text

    return {"project": project, "member_id": member_id}


def test_member_add_creates_notification(http, reader_token, member_added):
    def find_notification():
        response = http.get(
            f"{NOTIFICATIONS_URL}/api/v1/notifications/",
            params={"limit": 100},
            headers=auth(reader_token),
        )
        assert response.status_code == 200, response.text
        return next(
            (
                n
                for n in response.json()
                if n["type"] == "PROJECT_MEMBER_ADD"
                and n["user_id"] == member_added["member_id"]
            ),
            None,
        )

    notification = eventually(
        find_notification, describe="PROJECT_MEMBER_ADD notification"
    )

    assert notification["subject"]
    assert notification["body"]
