from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth.auth_bearer import JWTBearer
from app.schemas.event_schema import EventResponse
from app.services.event_service import get_event_by_id, get_events

router = APIRouter(prefix="/events")


@router.get("/", response_model=List[EventResponse])
async def events_get(
    service: Optional[str] = Query(
        None, description="The service that generated the events"
    ),
    user_id: Optional[str] = Query(
        None, description="The user ID associated with the events"
    ),
    limit: int = Query(50, description="The maximum number of events to return"),
    offset: int = Query(
        0,
        description="The number of events to skip before starting to collect the results",
    ),
):
    try:

        events = await get_events(
            service=service, user_id=user_id, limit=limit, offset=offset
        )

        return events

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{event_id}", response_model=EventResponse)
async def events_get_by_id(event_id: str):

    try:
        event = await get_event_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        return event
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
