from aio_pika import logger
from app.constants.task_event_types import TaskEventType
from app.templates import NotificationContent
from app.templates.task_create_template import task_create_template
TASK_NOTIFICATION_BUILDERS = {
    TaskEventType.TASK_CREATE:task_create_template,
    TaskEventType.TASK_UPDATE:print("task update triggered!"),
    TaskEventType.TASK_ASSIGN:print("task assign triggered!"),
    TaskEventType.TASK_UNASSIGN:print("task unassign triggered!"),
}


def _dispatch(payload):
    try:
        action = TaskEventType(payload["action"])
    except ValueError:
        print(f"Unknown event {payload['action']}")
        return

    builder = TASK_NOTIFICATION_BUILDERS.get(action)

    if builder:
        data = payload["metadata"]
        content = builder(
            username=data["username"],
            task_name=data["task_title"],
            actor_name=data["actor_username"],
        )
        # TODO Create create_mail send_mail functions in the new mail_service

