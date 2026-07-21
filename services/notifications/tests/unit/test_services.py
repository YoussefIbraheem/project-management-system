from datetime import datetime, timezone

from app.models.email_log import EmailStatus
from app.services.email_log_service import (
    create_email_log,
    delete_email_log,
    get_email_log,
    list_email_logs,
    update_email_log,
)
from app.services.notification_service import (
    create_notification,
    delete_notification,
    get_notification,
    list_notifications,
    update_notification,
)
from app.services.user_replica_service import (
    check_user_replica_exists,
    create_user_replica,
    delete_user_replica,
    fetch_users_replicas_by_ids,
    get_user_replica_by_id,
    list_users_replicas,
    update_user_replica,
)


def test_user_replica_crud_flow():
    created = create_user_replica(
        user_id="user-1",
        username="alice",
        email="alice@example.com",
        display_name="Alice",
    )
    assert created.user_id == "user-1"
    assert created.username == "alice"

    listed = list_users_replicas()
    assert len(listed) == 1

    fetched = get_user_replica_by_id("user-1")
    assert fetched is not None
    assert fetched.email == "alice@example.com"

    updated = update_user_replica(
        user_id="user-1",
        username="alice-updated",
        email="alice+updated@example.com",
        display_name="Alice Updated",
    )
    assert updated.username == "alice-updated"
    assert updated.display_name == "Alice Updated"

    same_or_new = check_user_replica_exists(
        user_id="user-1",
        username="ignored",
        email="ignored@example.com",
        display_name=None,
    )
    assert same_or_new.user_id == "user-1"
    assert same_or_new.username == "alice-updated"

    deleted = delete_user_replica("user-1")
    assert deleted is None
    assert get_user_replica_by_id("user-1") is None


def test_fetch_users_replicas_by_ids_returns_matching_subset():
    create_user_replica("user-1", "alice", "alice@example.com", "Alice")
    create_user_replica("user-2", "bob", "bob@example.com", "Bob")

    matches = fetch_users_replicas_by_ids(["user-2", "missing", "user-1"])

    assert {user.user_id for user in matches} == {"user-1", "user-2"}


def test_notification_crud_flow():
    create_user_replica("user-1", "alice", "alice@example.com", "Alice")

    created = create_notification(
        user_id="user-1",
        type="TASK_CREATE",
        body="A task was created",
        subject="Task created",
    )
    assert created.user_id == "user-1"
    assert created.type == "TASK_CREATE"

    listed = list_notifications()
    assert len(listed) == 1

    fetched = get_notification(created.id)
    assert fetched is not None
    assert fetched.subject == "Task created"

    updated = update_notification(
        notification_id=created.id,
        subject="Task created again",
        is_read=True,
    )
    assert updated.subject == "Task created again"
    assert updated.is_read is True

    assert delete_notification(created.id) is True


def test_email_log_crud_flow():
    create_user_replica("user-1", "alice", "alice@example.com", "Alice")
    notification = create_notification(
        user_id="user-1",
        type="TASK_UPDATE",
        body="A task was updated",
        subject="Task updated",
    )

    created = create_email_log(
        notification_id=notification.id,
        email_address="sender@example.com",
        recipient_email="alice@example.com",
    )
    assert created.status == EmailStatus.PENDING.value
    assert created.attempts == 0

    listed = list_email_logs(notification_id=notification.id)
    assert len(listed) == 1

    fetched = get_email_log(created.id)
    assert fetched is not None
    assert fetched.recipient_email == "alice@example.com"

    sent_at = datetime.now(timezone.utc)
    updated = update_email_log(
        email_log_id=created.id,
        status=EmailStatus.SENT.value,
        attempts=2,
        sent_at=sent_at,
    )
    assert updated.status == EmailStatus.SENT.value
    assert updated.attempts == 2
    assert updated.sent_at is not None

    assert delete_email_log(created.id) is True
    assert get_email_log(created.id) is None
