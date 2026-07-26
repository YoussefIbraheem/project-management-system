from datetime import datetime, timezone

from sqlmodel import SQLModel


def utc_now():
    return datetime.now(timezone.utc) 

class Base(SQLModel):
    pass