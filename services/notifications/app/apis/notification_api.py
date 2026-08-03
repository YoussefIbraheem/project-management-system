from fastapi import APIRouter, Depends

from app.auth.auth_bearer import JWTBearer
from app.services.notification_service import get_notification, list_notifications

router = APIRouter(prefix="/notifications",dependencies=[Depends(JWTBearer())],)


@router.get("/")
def notification_list(limit: int = 10, offset: int = 0):
    try:

        return list_notifications(limit=limit, offset=offset)
    except Exception as e:
        print(f"Error fetching notifications: {e}")
        return []


@router.get("/{notification_id}",dependencies=[Depends(JWTBearer())],)
def notification_get(notification_id: str):
    try:
        return get_notification(notification_id)
    except Exception as e:
        print(f"Error retrieving notification: {e}")
        return None
