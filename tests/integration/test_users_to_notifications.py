from conftest import NOTIFICATIONS_URL, auth, eventually


def test_registration_creates_user_replica(http, reader_token, registered_user):
    def find_replica():
        response = http.get(
            f"{NOTIFICATIONS_URL}/api/v1/users_replicas/{registered_user['id']}",
            headers=auth(reader_token),
        )
        assert response.status_code == 200, response.text
        return response.json()

    replica = eventually(find_replica, describe="user replica in notifications")

    assert replica["user_id"] == registered_user["id"]
    assert replica["email"] == registered_user["email"]
    assert replica["username"] == registered_user["username"]


def test_replica_metadata_keys_match_handler_signature(http, reader_token, registered_user):
    # * The dispatcher calls create_user_replica(**payload['metadata']).


    def find_replica():
        response = http.get(
            f"{NOTIFICATIONS_URL}/api/v1/users_replicas/{registered_user['id']}",
            headers=auth(reader_token),
        )
        assert response.status_code == 200, response.text
        return response.json()

    replica = eventually(find_replica, describe="user replica in notifications")

    expected_display_name = f"{registered_user['first_name']} {registered_user['last_name']}"
    assert replica["display_name"] == expected_display_name
