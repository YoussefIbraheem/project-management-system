from app.core.config import settings
from sqlmodel import SQLModel, create_engine , Session
from typing import Annotated
from fastapi import Depends

engine = create_engine(url=settings.DB_URL) # type: ignore

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]