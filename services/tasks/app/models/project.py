from sqlalchemy import Column, DateTime, Integer, String, Text, event, inspect
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from utils.publisher import publish_history_event

from app.events.project_event import (
    ProjectCreatedEvent,
    ProjectDeletedEvent,
    ProjectUpdatedEvent,
)

from .. import logger
from . import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_id = Column(String(255), nullable=False, index=True)

    boards = relationship(
        "Board", back_populates="project", cascade="all, delete-orphan"
    )


# ORM EVENTS

# @event.listens_for(Project, "after_insert")
# def project_created(mapper, connection, target):
#     """Publish a project created event to the message broker."""
#     event = ProjectCreatedEvent(
#         project_name=target.name,
#         owner_id=target.owner_id,
#         description=target.description,
#     )

#     publish_history_event(event.to_dict())


# @event.listens_for(Project, "after_update")
# def project_updated(mapper, connection, target):
#     """Publish a project updated event to the message broker."""
#     # Get all attributes that have been changed and publish them as events
    
#     inspected_attrs = inspect(target).attrs
#     updated_fields = []

#     for attr in inspected_attrs:
#         attr_history = attr.history

#         if not attr_history.added:
#             continue

#         old_value = attr.history.deleted[0]
#         new_value = attr.history.added[0]
#         updated_fields.append(
#             {"name": attr.key, "old_value": old_value, "new_value": new_value}
#         )
#         logger.info(f"{attr.key} changed from {old_value} to {new_value}")

#     if not updated_fields:
#         return

#     event = ProjectUpdatedEvent(owner_id=target.owner_id, updated_fields=updated_fields)

#     publish_history_event(event.to_dict())


# @event.listens_for(Project, "after_delete")
# def project_deleted(mapper, connection, target):
#     """Publish a project deleted event to the message broker."""
    
#     event = ProjectDeletedEvent(project_name=target.name, owner_id=target.owner_id)

#     publish_history_event(event.to_dict())
