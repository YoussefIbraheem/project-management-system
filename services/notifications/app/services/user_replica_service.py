from app.db.database import SessionDep
from sqlmodel import select
from app.models.user_replica import UserReplica

def list_users_replicas(session: SessionDep,limit: int = 10, offset: int = 0):
    query = select(UserReplica).offset(offset).limit(limit)
    
    users_replicas = session.exec(query).all()
    
    return users_replicas
    