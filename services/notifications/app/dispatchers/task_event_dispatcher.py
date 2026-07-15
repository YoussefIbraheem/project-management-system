from aio_pika import logger

from app.constants.task_event_types import TaskEventType

TASK_EVENT_HANDLERS = {
    TaskEventType.TASK_CREATE:print("task create triggered!"),
    TaskEventType.TASK_UPDATE:print("task update triggered!"),
    TaskEventType.TASK_MEMBER_ASSIGN:print("task assign triggered!"),
    TaskEventType.TASK_MEMBER_UNASSIGN:print("task unassign triggered!"),
}


def _dispatch(payload):
    try:
        action = TaskEventType(payload["action"])
    except ValueError:
        print(f"Unknown event {payload['action']}")
        return

    handler = TASK_EVENT_HANDLERS.get(action)

    if handler:
        data = payload["metadata"]
        handler(**data)

