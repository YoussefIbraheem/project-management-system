import asyncio
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from app.constants.task_event_types import TaskEventType
from app.constants.user_event_types import UserEventType
from app.dispatchers import task_event_dispatcher, user_event_dispatcher
from app.templates import NotificationContent, TaskNotificationContext


@pytest.mark.parametrize(
    ("event_type", "metadata"),
    [
        (UserEventType.USER_REGISTER, {"user_id": "1", "username": "alice", "email": "a@example.com", "display_name": "Alice"}),
        (UserEventType.USER_PROFILE_UPDATE, {"user_id": "1", "username": "alice2", "email": "a2@example.com", "display_name": "Alice 2"}),
        (UserEventType.USER_DELETE, {"user_id": "1", "username": "alice", "email": "a@example.com", "display_name": "Alice"}),
        (UserEventType.USER_LOGIN, {"user_id": "1", "username": "alice", "email": "a@example.com", "display_name": "Alice"}),
    ],
)
def test_user_dispatch_routes_payload_to_handler(monkeypatch, event_type, metadata):
    handler = Mock()
    monkeypatch.setitem(user_event_dispatcher.USER_EVENT_HANDLERS, event_type, handler)

    user_event_dispatcher._dispatch({"action": event_type.value, "metadata": metadata})

    handler.assert_called_once_with(**metadata)


def test_user_dispatch_ignores_unknown_action(monkeypatch):
    error = Mock()
    monkeypatch.setattr(user_event_dispatcher.rmq_logger, "error", error)

    user_event_dispatcher._dispatch({"action": "NOT_REAL", "metadata": {}})

    error.assert_called_once()


def test_task_dispatch_ignores_unknown_action(monkeypatch):
    info = Mock()
    monkeypatch.setattr(task_event_dispatcher.rmq_logger, "info", info)

    asyncio.run(task_event_dispatcher._dispatch({"action": "NOT_REAL", "metadata": {}}))

    info.assert_called()


def test_task_dispatch_creates_notifications_and_sends_email(monkeypatch):
    recipients = [
        SimpleNamespace(user_id="1", email="alice@example.com", username="alice")
    ]
    actor = SimpleNamespace(username="bob")
    created_notifications = []
    updated_notifications = []
    sent_contents = []

    def builder(ctx):
        return NotificationContent(
            recipient_email=ctx.recipient_email,
            subject=f"Task {ctx.task_title} created",
            body=f"Hi {ctx.username}, {ctx.actor_username} created {ctx.task_title}",
        )

    monkeypatch.setitem(
        task_event_dispatcher.TASK_NOTIFICATION_BUILDERS,
        TaskEventType.TASK_CREATE,
        (builder, TaskNotificationContext),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "fetch_users_replicas_by_ids",
        Mock(return_value=recipients),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "get_user_replica_by_id",
        Mock(return_value=actor),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "create_notification",
        Mock(
            side_effect=lambda **kwargs: created_notifications.append(kwargs)
            or SimpleNamespace(id=77)
        ),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "update_notification",
        Mock(side_effect=lambda **kwargs: updated_notifications.append(kwargs)),
    )

    class FakeEmailService:
        def __init__(self, **kwargs):  # noqa: ARG002
            pass

        async def send_email(self, content):
            sent_contents.append(content)
            return True

    monkeypatch.setattr(task_event_dispatcher, "EmailService", FakeEmailService)

    payload = {
        "action": TaskEventType.TASK_CREATE.value,
        "actor_id": "1",
        "metadata": {
            "recipients_ids": ["1"],
            "task_title": "Build API",
            "project_name": "Platform",
        },
    }

    asyncio.run(task_event_dispatcher._dispatch(payload))

    assert created_notifications == [
        {
            "user_id": "1",
            "type": TaskEventType.TASK_CREATE.value,
            "body": "Hi alice, bob created Build API",
            "subject": "Task Build API created",
        }
    ]
    assert sent_contents[0].notification_id == 77
    assert updated_notifications == [{"notification_id": 77, "is_read": True}]


def test_task_dispatch_skips_when_no_recipients(monkeypatch):
    create_notification = Mock()
    send_email = Mock()

    monkeypatch.setattr(
        task_event_dispatcher,
        "fetch_users_replicas_by_ids",
        Mock(return_value=[]),
    )
    monkeypatch.setattr(task_event_dispatcher, "create_notification", create_notification)
    monkeypatch.setattr(task_event_dispatcher, "EmailService", send_email)

    asyncio.run(
        task_event_dispatcher._dispatch(
            {
                "action": TaskEventType.TASK_CREATE.value,
                "actor_id": "1",
                "metadata": {
                    "recipients_ids": ["999"],
                    "task_title": "Build API",
                    "project_name": "Platform",
                },
            }
        )
    )

    create_notification.assert_not_called()
    send_email.assert_not_called()


def test_task_dispatch_falls_back_to_private_user_when_actor_missing(monkeypatch):
    recipients = [
        SimpleNamespace(user_id="1", email="alice@example.com", username="alice")
    ]
    captured = {}

    def builder(ctx):
        captured["actor_username"] = ctx.actor_username
        return NotificationContent(
            recipient_email=ctx.recipient_email,
            subject="Task Build API updated",
            body="body",
        )

    monkeypatch.setitem(
        task_event_dispatcher.TASK_NOTIFICATION_BUILDERS,
        TaskEventType.TASK_UPDATE,
        (builder, TaskNotificationContext),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "fetch_users_replicas_by_ids",
        Mock(return_value=recipients),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "get_user_replica_by_id",
        Mock(return_value=None),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "create_notification",
        Mock(return_value=SimpleNamespace(id=88)),
    )
    monkeypatch.setattr(
        task_event_dispatcher,
        "update_notification",
        Mock(),
    )

    class FakeEmailService:
        def __init__(self, **kwargs):  # noqa: ARG002
            pass

        async def send_email(self, content):
            return True

    monkeypatch.setattr(task_event_dispatcher, "EmailService", FakeEmailService)

    asyncio.run(
        task_event_dispatcher._dispatch(
            {
                "action": TaskEventType.TASK_UPDATE.value,
                "actor_id": "missing",
                "metadata": {
                    "recipients_ids": ["1"],
                    "task_title": "Build API",
                    "project_name": "Platform",
                },
            }
        )
    )

    assert captured["actor_username"] == "Private User"
