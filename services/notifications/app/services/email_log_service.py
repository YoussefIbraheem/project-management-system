from datetime import datetime

from sqlmodel import select

from app.db.database import Session, engine
from app.models.email_log import EmailLog, EmailStatus
from app.schemas.email_log_schema import EmailLogSchema


def list_email_logs(
    notification_id: int | None = None, limit: int = 10, offset: int = 0
):
    with Session(engine) as session:
        query = select(EmailLog).offset(offset).limit(limit)
        if notification_id:
            query = query.where(EmailLog.notification_id == notification_id)

        email_logs = session.exec(query).all()  # type: ignore

        return [EmailLogSchema.model_validate(el) for el in email_logs]


def get_email_log(email_log_id: int):
    with Session(engine) as session:
        query = select(EmailLog).where(EmailLog.id == email_log_id)
        email_logs = session.exec(query).first()  # type: ignore

        return EmailLogSchema.model_validate(email_logs) if email_logs else None


def create_email_log(
    notification_id: int,
    email_address: str,
    recipient_email: str,
    status: str = EmailStatus.PENDING.value,
    error_message: str | None = None,
    attempts: int = 0,
    sent_at: datetime | None = None,
):
    with Session(engine) as session:
        new_email_log = EmailLog(
            notification_id=notification_id,
            email_address=email_address,
            recipient_email=recipient_email,
            status=status,
            error_message=error_message,
            attempts=attempts,
            sent_at=sent_at,
        )
        session.add(new_email_log)
        session.commit()
        session.refresh(new_email_log)

        return EmailLogSchema.model_validate(new_email_log)


def update_email_log(
    email_log_id: int,
    status: str | None,
    attempts: int | None,
    error_message: str | None = None,
    sent_at: datetime | None = None,
):
    with Session(engine) as session:
        query = select(EmailLog).where(EmailLog.id == email_log_id)
        email_logs = session.exec(query).first()  # type: ignore

        if not email_logs:
            return None
        email_logs.status = status or email_logs.status
        email_logs.attempts = attempts or email_logs.attempts
        email_logs.error_message = error_message or email_logs.error_message
        email_logs.sent_at = sent_at or email_logs.sent_at
        session.commit()
        session.refresh(email_logs)

        return EmailLogSchema.model_validate(email_logs)


def delete_email_log(email_log_id: int):
    with Session(engine) as session:
        query = select(EmailLog).where(EmailLog.id == email_log_id)
        email_logs = session.exec(query).first()  # type: ignore

        if email_logs:
            session.delete(email_logs)
            session.commit()
            return True

        return False
