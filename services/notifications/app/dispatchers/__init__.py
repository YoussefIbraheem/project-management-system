import asyncio
from inspect import iscoroutinefunction

from .task_event_dispatcher import _dispatch as _dispatch_task
from .user_event_dispatcher import _dispatch as _dispatch_user

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

    if iscoroutinefunction(dispatcher):
        asyncio.create_task(dispatcher(payload))
    else:
        dispatcher(payload)
