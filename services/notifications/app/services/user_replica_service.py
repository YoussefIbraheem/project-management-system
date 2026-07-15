from typing import Optional

from sqlmodel import select

from app.db.database import Session, engine

from app.models.user_replica import UserReplica
from app.schemas.user_replica_schema import (
    UserReplicaSchema,
)


def list_users_replicas(limit: int = 10, offset: int = 0):
    with Session(engine) as session:
        query = select(UserReplica).offset(offset).limit(limit)

        users_replicas = session.exec(query).all()

        return [UserReplicaSchema.model_validate(user) for user in users_replicas]


def get_user_replica(user_id: str):
    with Session(engine) as session:
        query = select(UserReplica).where("user_id" == user_id)

        user_replica = session.exec(query).first()
        if not user_replica:
            return None
        return UserReplicaSchema.model_validate(user_replica)


def create_user_replica(
    user_id: str,
    username: str,
    email: str,
    display_name: Optional[str],
):
    with Session(engine) as session:
        new_user_replica = UserReplica(
            user_id=user_id,
            username=username,
            email=email,
            display_name=display_name,
        )
        session.add(new_user_replica)
        session.commit()
        session.refresh(new_user_replica)

        return UserReplicaSchema.model_validate(new_user_replica)


def check_user_replica_exists(
    user_id: str,
    username: str,
    email: str,
    display_name: Optional[str],
):
    with Session(engine) as session:
        query = select(UserReplica).where("user_id" == user_id)
        new_user_replica = session.exec(query).first()

        if not new_user_replica:
            return create_user_replica(user_id, username, email, display_name)

        return UserReplicaSchema.model_validate(new_user_replica)


def update_user_replica(
    user_id: str,
    username: str,
    email: str,
    display_name: Optional[str],
):
    with Session(engine) as session:
        query = select(UserReplica).where("user_id" == user_id)
        user_replica = session.exec(query).first()

        if not user_replica:
            raise ValueError(f"No user replica found with id {user_id}")

        updateables = {
            "username": username,
            "email": email,
            "display_name": display_name,
        }

        for key, value in updateables.items():
            if value is not None:
                setattr(user_replica, key, value)

        session.commit()
        session.refresh(user_replica)

        return UserReplicaSchema.model_validate(user_replica)


def delete_user_replica(user_id: str):
    with Session(engine) as session:
        query = select(UserReplica).where("user_id" == user_id)
        user_replica = session.exec(query).first()

        if not user_replica:
            raise ValueError(f"No user replica found with id {user_id}")

        session.delete(user_replica)
        session.commit()
