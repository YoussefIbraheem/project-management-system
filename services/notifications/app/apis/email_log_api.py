from fastapi import APIRouter, Depends

from app.auth.auth_bearer import JWTBearer
from app.services.email_log_service import get_email_log, list_email_logs

router = APIRouter(prefix="/email-logs")


@router.get(
    "/",
    dependencies=[Depends(JWTBearer())],
)
def email_logs_list(
    notification_id: int | None = None, limit: int = 10, offset: int = 0
):
    try:
        return list_email_logs(
            notification_id=notification_id, limit=limit, offset=offset
        )
    except Exception as e:
        return {"error": str(e)}


@router.get(
    "/{email_log_id}",
    dependencies=[Depends(JWTBearer())],
)
def email_logs_detail(email_log_id: int):
    try:
        return get_email_log(email_log_id=email_log_id)
    except Exception as e:
        return {"error": str(e)}
