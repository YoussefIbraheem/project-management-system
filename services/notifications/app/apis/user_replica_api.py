from fastapi import APIRouter, HTTPException

from app.services.user_replica_service import (
    get_user_replica_by_id,
    list_users_replicas,
)

router = APIRouter(prefix="/users_replicas")


@router.get("/")
def users_replicas_list(limit: int = 100, offset: int = 0):
    try:
        return list_users_replicas(limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{user_id}")
def users_replica_by_user_id(user_id: str):
    try:
        return get_user_replica_by_id(user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
