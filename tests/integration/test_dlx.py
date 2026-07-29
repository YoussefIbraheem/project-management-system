import time
import uuid

from conftest import HISTORY_URL, NOTIFICATIONS_URL, USERS_URL, auth, eventually, publish_raw

# Comfortably below the 1000ms x-message-ttl on the main queues, so a pass
# here is only possible if delivery does NOT route through the DLX's TTL.
HAPPY_PATH_BUDGET = 0.8


def test_history_event_is_delivered_without_the_dlx_ttl_delay(http, reader_token):
    suffix = uuid.uuid4().hex[:10]
    payload = {
        "email": f"dlx_latency_{suffix}@example.com",
        "username": f"dlx_latency_{suffix}",
        "password": "DlxLatency1",
        "password_confirm": "DlxLatency1",
    }

    t0 = time.monotonic()
    response = http.post(f"{USERS_URL}/api/v1/register/", json=payload)
    assert response.status_code == 201, response.text

    def find_event():
        resp = http.get(
            f"{HISTORY_URL}/api/v1/events/",
            params={"service": "users"},
            headers=auth(reader_token),
        )
        assert resp.status_code == 200, resp.text
        for event in resp.json():
            if event.get("metadata", {}).get("email") == payload["email"]:
                return event
        return None

    eventually(find_event, timeout=5.0, describe="registration event in history")
    elapsed = time.monotonic() - t0

    assert elapsed < HAPPY_PATH_BUDGET, (
        f"delivery took {elapsed:.3f}s — the main queue's TTL should not be "
        "on the happy-path latency budget"
    )


def test_notification_replica_sync_is_delivered_without_the_dlx_ttl_delay(
    http, reader_token, admin_token
):
    suffix = uuid.uuid4().hex[:10]
    payload = {
        "email": f"dlx_latency_{suffix}@example.com",
        "username": f"dlx_latency_{suffix}",
        "password": "DlxLatency1",
        "password_confirm": "DlxLatency1",
    }

    t0 = time.monotonic()
    response = http.post(f"{USERS_URL}/api/v1/register/", json=payload)
    assert response.status_code == 201, response.text

    listing = http.get(
        f"{USERS_URL}/api/v1/users/",
        params={"email": payload["email"]},
        headers=auth(admin_token),
    )
    assert listing.status_code == 200 and listing.json(), listing.text
    user_id = str(listing.json()[0]["id"])

    def find_replica():
        resp = http.get(
            f"{NOTIFICATIONS_URL}/api/v1/users_replicas/{user_id}",
            headers=auth(reader_token),
        )
        assert resp.status_code == 200, resp.text
        return resp.json()

    eventually(find_replica, timeout=5.0, describe="user replica in notifications")
    elapsed = time.monotonic() - t0

    assert elapsed < HAPPY_PATH_BUDGET, (
        f"delivery took {elapsed:.3f}s — the main queue's TTL should not be "
        "on the happy-path latency budget"
    )


def test_malformed_history_message_does_not_block_subsequent_processing(http, reader_token):
    # Missing every required EventCreate field except `service` — guaranteed
    # to raise inside create_event, on both the main_queue attempt and the
    # one bonus dlx_queue retry.
    publish_raw(
        exchange="mainhistoryexchange",
        routing_key="history",
        body={
            "task": "app.consumers.history_consumer.record_activity",
            "id": str(uuid.uuid4()),
            "args": [{"service": "integration-test-poison"}],
            "kwargs": {},
            "retries": 0,
        },
    )

    suffix = uuid.uuid4().hex[:10]
    payload = {
        "email": f"after_poison_{suffix}@example.com",
        "username": f"after_poison_{suffix}",
        "password": "AfterPoison1",
        "password_confirm": "AfterPoison1",
    }
    response = http.post(f"{USERS_URL}/api/v1/register/", json=payload)
    assert response.status_code == 201, response.text

    def find_event():
        resp = http.get(
            f"{HISTORY_URL}/api/v1/events/",
            params={"service": "users"},
            headers=auth(reader_token),
        )
        assert resp.status_code == 200, resp.text
        for event in resp.json():
            if event.get("metadata", {}).get("email") == payload["email"]:
                return event
        return None

    eventually(
        find_event,
        timeout=5.0,
        describe="a legitimate event published right after a poison message",
    )


def test_malformed_task_notification_message_does_not_block_subsequent_processing(
    http, reader_token, admin_token
):
    # A recognised task action with metadata missing recipients_ids —
    # task_event_dispatcher._dispatch does data["recipients_ids"] with no
    # guard, so this raises a KeyError on both attempts.
    publish_raw(
        exchange="mainnotificationsexchange",
        routing_key="notifications",
        body={
            "task": "app.consumers.notifications_consumer.record_activity",
            "id": str(uuid.uuid4()),
            "args": [
                {
                    "actor_id": "integration-test",
                    "service": "tasks",
                    "action": "PROJECT_MEMBER_ADD",
                    "subject_id": "1",
                    "subject_type": "PROJECT",
                    "metadata": {"project_name": "poison"},
                }
            ],
            "kwargs": {},
            "retries": 0,
        },
    )

    suffix = uuid.uuid4().hex[:10]
    payload = {
        "email": f"after_poison_{suffix}@example.com",
        "username": f"after_poison_{suffix}",
        "password": "AfterPoison1",
        "password_confirm": "AfterPoison1",
    }
    response = http.post(f"{USERS_URL}/api/v1/register/", json=payload)
    assert response.status_code == 201, response.text

    listing = http.get(
        f"{USERS_URL}/api/v1/users/",
        params={"email": payload["email"]},
        headers=auth(admin_token),
    )
    assert listing.status_code == 200 and listing.json(), listing.text
    user_id = str(listing.json()[0]["id"])

    def find_replica():
        resp = http.get(
            f"{NOTIFICATIONS_URL}/api/v1/users_replicas/{user_id}",
            headers=auth(reader_token),
        )
        assert resp.status_code == 200, resp.text
        return resp.json()

    eventually(
        find_replica,
        timeout=5.0,
        describe="a legitimate replica sync published right after a poison message",
    )
