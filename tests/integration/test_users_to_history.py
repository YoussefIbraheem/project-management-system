"""users service -> RabbitMQ 'history' queue -> history service."""

from conftest import eventually


def test_registration_lands_in_history(registered_user, history_events):
    def find_event():
        events = history_events(service="users", actor_id=registered_user["id"])
        return next((e for e in events if e["action"] == "USER_REGISTER"), None)

    event = eventually(find_event, describe="USER_REGISTER event in history")

    assert event["service"] == "users"
    assert event["subject_id"] == registered_user["id"]
    assert event["metadata"]["email"] == registered_user["email"]
    assert event["metadata"]["username"] == registered_user["username"]


def test_history_event_carries_required_envelope_fields(registered_user, history_events):
    def find_event():
        events = history_events(service="users", actor_id=registered_user["id"])
        return next((e for e in events if e["action"] == "USER_REGISTER"), None)

    event = eventually(find_event, describe="USER_REGISTER event in history")

    # The consumer builds EventCreate from the raw payload; a producer that
    # drops any of these silently fails validation inside the worker.
    for field in ("actor_id", "service", "action", "subject_id", "subject_type", "metadata"):
        assert event[field] is not None, f"{field} missing from persisted event"
    assert event["timestamp"]


def test_history_read_api_rejects_non_superuser(http, registered_user):
    from conftest import HISTORY_URL, auth, mint_token

    token = mint_token(registered_user["id"], is_superuser=False)
    response = http.get(f"{HISTORY_URL}/api/v1/events/", headers=auth(token))

    assert response.status_code == 403
