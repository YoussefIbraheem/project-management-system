from aio_pika import logger

from app.constants.user_event_types import UserEventType
from app.schemas.user_replica_schema import UserReplicaCreateSchema
from app.services.user_replica_service import (
    create_user_replica,
    delete_user_replica,
    update_user_replica,
    check_user_replica_exists,
)

USER_EVENT_HANDLERS = {
    UserEventType.USER_REGISTER: create_user_replica,
    UserEventType.USER_PROFILE_UPDATE: update_user_replica,
    UserEventType.USER_DELETE: delete_user_replica,
    UserEventType.USER_LOGIN: check_user_replica_exists,  # NOTE:: A replica check is done in the login service
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
