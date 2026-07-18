from app.constants.task_event_types import TaskEventType
from app.templates import NotificationContext
from app.templates.task_create_template import task_create_template
from app.templates.task_update_template import task_update_template
from app.templates.task_assign_template import task_assign_template
from app.templates.task_unassign_template import task_unassign_template
from app.services.user_replica_service import (
    fetch_users_replicas_by_ids,
    get_user_replica_by_id,
)
from app.services.notification_service import create_notification, update_notification
from utils.mailer import send_email
from app import rmq_logger

TASK_NOTIFICATION_BUILDERS = {
    TaskEventType.TASK_CREATE: task_create_template,
    TaskEventType.TASK_UPDATE: task_update_template,
    TaskEventType.TASK_ASSIGN: task_assign_template,
    TaskEventType.TASK_UNASSIGN: task_unassign_template,
}

async def _dispatch(payload):
    try:
        action = TaskEventType(payload["action"])
    except ValueError:
        rmq_logger.info(f"Unknown event {payload['action']}")
        return

    builder = TASK_NOTIFICATION_BUILDERS.get(action)
    if builder:
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
            ctx = NotificationContext(
                recipient_email=recipient.email,
                username=recipient.username,
                task_title=data["task_title"],
                actor_username=actor_username,
                project_name=data["project_name"],
            )
            content = builder(ctx)
            notification = create_notification(
                user_id=recipient.user_id,
                type=action.value,
                body=content.body,
                subject=content.subject,
            )
            rmq_logger.info(f"Sending email to {recipient.email}")
            result = await send_email(content)
            if result:
                update_notification(
                    notification_id=notification.id,
                    is_read=True,
                )
                
        # TODO Create create_mail send_mail functions in the new mail_service
