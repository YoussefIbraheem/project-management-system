from dataclasses import fields

from aiosmtplib import SMTP
from utils.mailer import EmailService

from app import rmq_logger
from app.constants.task_event_types import TaskEventType
from app.core.config import settings
from app.services.notification_service import create_notification, update_notification
from app.services.user_replica_service import (
    fetch_users_replicas_by_ids,
    get_user_replica_by_id,
)
from app.templates import ProjectNotificationContext, TaskNotificationContext
from app.templates.project_member_add_template import project_member_add_template
from app.templates.project_member_remove_template import project_member_remove_template
from app.templates.task_assign_template import task_assign_template
from app.templates.task_create_template import task_create_template
from app.templates.task_unassign_template import task_unassign_template
from app.templates.task_update_template import task_update_template

TASK_NOTIFICATION_BUILDERS = {
    TaskEventType.TASK_CREATE: (task_create_template, TaskNotificationContext),
    TaskEventType.TASK_UPDATE: (task_update_template, TaskNotificationContext),
    TaskEventType.TASK_ASSIGN: (task_assign_template, TaskNotificationContext),
    TaskEventType.TASK_UNASSIGN: (task_unassign_template, TaskNotificationContext),
    TaskEventType.PROJECT_MEMBER_ADD: (project_member_add_template,ProjectNotificationContext),
    TaskEventType.PROJECT_MEMBER_DELETE: (project_member_remove_template,ProjectNotificationContext),
}


def _build_context(context_cls, *, recipient, actor_username, data):
    values = {
        "recipient_email": recipient.email,
        "username": recipient.username,
        "actor_username": actor_username,
        **data,
    }
    field_names = {f.name for f in fields(context_cls)}
    return context_cls(**{k: v for k, v in values.items() if k in field_names})


async def _dispatch(payload):
    try:
        action = TaskEventType(payload["action"])
    except ValueError:
        rmq_logger.info(f"Unknown event {payload['action']}")
        return
    builder = TASK_NOTIFICATION_BUILDERS.get(action)
    if builder:
        template, ContextClass = builder
        rmq_logger.info(f"Building notification for {action}")
        data = payload["metadata"]
        recipients = fetch_users_replicas_by_ids(data["recipients_ids"])
        rmq_logger.info(f"Fetched recipients: {recipients}")

        if not recipients:
            rmq_logger.info("No recipients found")
            return

        actor_data = get_user_replica_by_id(payload["actor_id"])
        actor_username = actor_data.username if actor_data else "Private User"
        rmq_logger.info("Building notification content...")
        for recipient in recipients:

            ctx = _build_context(
                ContextClass,
                recipient=recipient,
                actor_username=actor_username,
                data=data,
            )
            content = template(ctx)
            notification = create_notification(
                user_id=recipient.user_id,
                type=action.value,
                body=content.body,
                subject=content.subject,
            )
            content.notification_id = notification.id
            rmq_logger.info(f"Sending email to {recipient.email}")
            service = EmailService(
                logger=rmq_logger, settings=settings, smtp_client_factory=SMTP
            )
            result = await service.send_email(content)
            if result:
                update_notification(
                    notification_id=notification.id,
                    is_read=True,
                )
