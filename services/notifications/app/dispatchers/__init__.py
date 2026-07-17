from aio_pika import logger

from .user_event_dispatcher import _dispatch as _dispatch_user
from .task_event_dispatcher import _dispatch as _dispatch_task

SERVICE_DISPATCHERS = {
    "users": _dispatch_user,
    "tasks":_dispatch_task
}


def dispatch(payload):
    print("Dispatching...")
    print(f"Payload: {payload}")
    service = payload["service"]
    dispatcher = SERVICE_DISPATCHERS.get(service)

    if not dispatcher:
        print(f"Unknown service {service}")
        return

    dispatcher(payload)
