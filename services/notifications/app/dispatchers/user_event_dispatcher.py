from aio_pika import logger

from app.constants.user_event_types import UserEventType
from app.services.user_replica_service import (
    create_user_replica,
    delete_user_replica,
    update_user_replica,
)

USER_EVENT_HANDLERS = {
    UserEventType.USER_REGISTER: create_user_replica,
    UserEventType.USER_PROFILE_UPDATE: update_user_replica,
    UserEventType.USER_DELETE: delete_user_replica,
}


def _dispatch(payload):
    try:
        action = UserEventType(payload["action"])
    except ValueError:
        print(f"Unknown event {payload['action']}")
        return

    handler = USER_EVENT_HANDLERS.get(action)

    if handler:
        data = payload["metadata"]
        handler(**data)
