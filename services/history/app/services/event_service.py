import re
from datetime import datetime, timezone
from typing import Optional

from app.models.event import Event
from app.schemas.event_schema import EventCreate, EventResponse


async def get_events(
    service: Optional[str] = None,
    actor_id: Optional[str] = None,
    metadata: Optional[str] = None,
    date: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    filters = []

    if service:
        filters.append(Event.service == service)
    if actor_id:
        filters.append(Event.actor_id == actor_id)
    if metadata:
        filters.append(re.compile(metadata, re.IGNORECASE))
    if date:
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        filters.append(Event.timestamp >= date_obj)

    query = Event.find(*filters)

    events = await query.sort(-Event.timestamp).skip(offset).limit(limit).to_list() #type: ignore

    return [EventResponse(**event.model_dump(by_alias=True)) for event in events]


async def get_event_by_id(event_id: str):

    event = await Event.get(event_id)

    if not event:
        return None

    return EventResponse(**event.model_dump(by_alias=True))


async def create_event(event_data: dict):

    event_create = EventCreate(**event_data)
    event = Event(
        actor_id=event_create.actor_id,
        service=event_create.service,
        action=event_create.action,
        subject_id=event_create.subject_id,
        subject_type=event_create.subject_type,
        metadata=event_create.metadata,
        timestamp=datetime.now(timezone.utc),
    )

    await event.insert()
    return str(event.id)
