from fastapi import APIRouter, HTTPException, Query

from app.schemas.event_schema import EventResponse
from app.services.event_service import get_event_by_id, get_events

router = APIRouter(prefix="/events")


@router.get("/", response_model=list[EventResponse])
async def events_get(
    service: str | None = Query(
        None, description="The service that generated the events"
    ),
    actor_id: str | None = Query(
        None, description="The user ID associated with the events"
    ),
    date: str | None = Query(
        None,
        description="The date range for the events starting from input data till current date (format: YYYY-MM-DD)",
    ),
    limit: int = Query(50, description="The maximum number of events to return"),
    offset: int = Query(
        0,
        description="The number of events to skip before starting to collect the results",
    ),
):
    try:
        events = await get_events(
            service=service,
            actor_id=actor_id,
            limit=limit,
            offset=offset,
            date=date,
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
