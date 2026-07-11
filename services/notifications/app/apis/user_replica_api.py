from fastapi import APIRouter, HTTPException, Query
from app.services.user_replica_service import list_users_replicas
from app.db.database import SessionDep
router = APIRouter(prefix="/users_replicas")

@router.get("/")
def users_replicas_list(session:SessionDep,limit: int = 100, offset: int = 0):
    try:
        return list_users_replicas(session,limit=limit, offset=offset)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
