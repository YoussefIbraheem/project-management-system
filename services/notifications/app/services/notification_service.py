from typing import Optional

from sqlmodel import select
from app.models.notification import Notification
from app.db.database import Session, engine
from app.schemas.notification_schema import NotificationSchema


def list_notifications(limit: int = 10, offset: int = 0):
    with Session(engine) as session:
        query = select(Notification).offset(offset).limit(limit)
        notifications = session.exec(query).all()

        return [NotificationSchema.model_validate(n) for n in notifications]


def get_notification(notification_id: str):
    with Session(engine) as session:
        query = select(Notification).where("id" == notification_id)
        notification = session.exec(query).first()
        if not notification:
            return None
        return NotificationSchema.model_validate(notification)


def create_notification(
    user_id: str,
    type: str,
    body: str,
    subject: Optional[str] = None,
    is_read: bool = False,
):
    with Session(engine) as session:
        new_notification = Notification(
            user_id=user_id,
            type=type,
            body=body,
            subject=subject,
            is_read=is_read,
        )

        session.add(Notification)
        session.commit()

        return NotificationSchema.model_validate(new_notification)


def update_notification(
    notification_id: int,
    type: Optional[str],
    body: Optional[str],
    subject: Optional[str] = None,
    is_read: Optional[bool] = False,
):
    with Session(engine) as session:
        query = select(Notification).where("id" == notification_id)
        notification = session.exec(query).first()

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
        query = select(Notification).where("id" == notification_id)
        notification = session.exec(query).first()
        if not notification:
            raise ValueError(f"Notification with id {notification_id} not found")
        session.delete(notification)
        session.commit()
        return True
