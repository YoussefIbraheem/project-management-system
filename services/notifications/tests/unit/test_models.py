from datetime import datetime

from app.models.email_log import EmailLog, EmailStatus
from app.models.notification import Notification
from app.models.user_replica import UserReplica


def test_user_replica_defaults_and_persistence(session):
    user = UserReplica(
        user_id="1",
        email="user@example.com",
        username="alice",
        display_name="Alice",
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    assert isinstance(user.created_at, datetime)
    assert user.updated_at is None
    assert user.display_name == "Alice"


def test_notification_links_to_user_and_email_logs(session):
    user = UserReplica(
        user_id="1",
        email="user@example.com",
        username="alice",
        display_name="Alice",
    )
    session.add(user)
    session.commit()

    notification = Notification(
        user_id=user.user_id,
        type="TASK_CREATE",
        subject="Task created",
        body="A task was created",
    )
    session.add(notification)
    session.commit()
    session.refresh(notification)

    email_log = EmailLog(
        email_address="sender@example.com",
        notification_id=notification.id,  # type: ignore[arg-type]
        recipient_email=user.email,
    )
    session.add(email_log)
    session.commit()
    session.refresh(email_log)

    loaded_notification = session.get(Notification, notification.id)
    assert loaded_notification is not None
    assert loaded_notification.user_replica.user_id == user.user_id
    assert loaded_notification.email_logs[0].recipient_email == user.email
    assert loaded_notification.is_read is False
    assert isinstance(loaded_notification.created_at, datetime)


def test_email_log_defaults_and_relationship(session):
    user = UserReplica(
        user_id="1",
        email="user@example.com",
        username="alice",
        display_name="Alice",
    )
    session.add(user)
    session.commit()

    notification = Notification(
        user_id=user.user_id,
        type="TASK_UPDATE",
        subject="Task updated",
        body="A task was updated",
    )
    session.add(notification)
    session.commit()

    email_log = EmailLog(
        email_address="sender@example.com",
        notification_id=notification.id,  # type: ignore[arg-type]
        recipient_email=user.email,
    )
    session.add(email_log)
    session.commit()
    session.refresh(email_log)

    loaded_email_log = session.get(EmailLog, email_log.id)
    assert loaded_email_log is not None
    assert loaded_email_log.status == EmailStatus.PENDING.value
    assert loaded_email_log.attempts == 0
    assert loaded_email_log.sent_at is None
    assert isinstance(loaded_email_log.created_at, datetime)
    assert loaded_email_log.notification.id == notification.id


def test_email_status_values_are_stable():
    assert EmailStatus.PENDING.value == "pending"
    assert EmailStatus.SENT.value == "sent"
    assert EmailStatus.FAILED.value == "failed"
    assert EmailStatus.RETRYING.value == "retrying"
