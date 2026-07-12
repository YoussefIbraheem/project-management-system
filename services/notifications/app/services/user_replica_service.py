from sqlmodel import select

from app.db.database import SessionDep
from app.models.user_replica import UserReplica
from app.schemas.user_replica_schema import UserReplicaCreateSchema, UserReplicaSchema, UserReplicaUpdateSchema


def list_users_replicas(session: SessionDep, limit: int = 10, offset: int = 0):
    query = select(UserReplica).offset(offset).limit(limit)

    users_replicas = session.exec(query).all()

    return [UserReplicaSchema.model_validate(user) for user in users_replicas]


def get_user_replica(session: SessionDep, user_id: str):

    query = select(UserReplica).where("user_id" == user_id)

    user_replica = session.exec(query).first()

    return UserReplicaSchema.model_validate(user_replica)


def create_user_replica(session:SessionDep,user_replica_data:UserReplicaCreateSchema):
    new_user_replica = UserReplica(
        user_id = user_replica_data.user_id,
        username=user_replica_data.username,
        email=user_replica_data.email,
        display_name=user_replica_data.display_name
    )
    session.add(new_user_replica)
    session.commit()
    session.refresh(new_user_replica)

    return UserReplicaSchema.model_validate(new_user_replica)


def update_user_replica(session:SessionDep,user_id:str,user_replica_data:UserReplicaUpdateSchema):
    query = select(UserReplica).where("user_id" == user_id)
    user_replica = session.exec(query).first()

    if not user_replica:
        raise ValueError(f"No user replica found with id {user_id}")

    for key, value in user_replica_data.model_dump():
        setattr(user_replica, key, value)

    session.commit()
    session.refresh(user_replica)

    return UserReplicaSchema.model_validate(user_replica)


def delete_user_replica(session:SessionDep,user_id:str):
    query = select(UserReplica).where("user_id" == user_id)
    user_replica = session.exec(query).first()

    if not user_replica:
        raise ValueError(f"No user replica found with id {user_id}")

    session.delete(user_replica)
    session.commit()