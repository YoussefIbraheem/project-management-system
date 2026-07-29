
from sqlmodel import select

from app.db.database import Session, engine
from app.models.notification import Notification
from app.models.user_replica import UserReplica
from app.schemas.notification_schema import NotificationSchema


def list_notifications(limit: int = 10, offset: int = 0):
    with Session(engine) as session:
        query = select(Notification).offset(offset).limit(limit)
        notifications = session.exec(query).all() #type: ignore

        return [NotificationSchema.model_validate(n) for n in notifications]


def get_notification(notification_id: str):
    with Session(engine) as session:
        query = select(Notification).where(Notification.id == notification_id)
        notification = session.exec(query).first() #type: ignore
        if not notification:
            return None
        return NotificationSchema.model_validate(notification)


def create_notification(
    user_id: str,
    type: str,
    body: str,
    subject: str | None = None,
    is_read: bool = False,
):
    with Session(engine) as session:
        user_replica_q = select(UserReplica).where(UserReplica.user_id == user_id)
        user_replica = session.exec(user_replica_q).first() #type: ignore
        if not user_replica:
            raise ValueError(f"No user found for user_id: {user_id}")
        new_notification = Notification(
            user_id=user_replica.user_id,
            type=type,
            subject=subject,
            body=body,
            is_read=is_read,
        )

        session.add(new_notification)
        session.commit()
        session.refresh(new_notification)

        return NotificationSchema.model_validate(new_notification)


def update_notification(
    notification_id: int,
    type: str | None = None,
    body: str | None = None,
    subject: str | None = None,
    is_read: bool | None = None,
):
    with Session(engine) as session:
        query = select(Notification).where(Notification.id == notification_id)
        notification = session.exec(query).first() #type: ignore

        if not notification:
            raise ValueError(f"Notification with id {notification_id} not found")

        updateables = {
            "type": type,
            "body": body,
            "subject": subject,
            "is_read": is_read,
        }

        for key, value in updateables.items():
            if value is not None:
                setattr(notification, key, value)

        session.commit()
        session.refresh(notification)

        return NotificationSchema.model_validate(notification)


def delete_notification(notification_id: int):
    with Session(engine) as session:
        query = select(Notification).where(Notification.id == notification_id)
        notification = session.exec(query).first() #type: ignore
        if not notification:
            raise ValueError(f"Notification with id {notification_id} not found")
        session.delete(notification)
        session.commit()
        return True
