from aio_pika import logger

from .user_event_dispatcher import _dispatch as _dispatch_user

SERVICE_DISPATCHERS = {
    "users": _dispatch_user,
}


def dispatch(payload):
    service = payload["service"]
    dispatcher = SERVICE_DISPATCHERS.get(service)

    if not dispatcher:
        print(f"Unknown service {service}")
        return

    return dispatcher(payload)
