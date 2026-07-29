from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ProjectBase(BaseModel):
    """Shared project fields used by project creation and response models."""
    name: str = Field(..., min_length=1, max_length=255, description="Project Name")
    description: str | None = Field(None, description="Project Description")
    
    model_config = ConfigDict(from_attributes=True)


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""


class ProjectUpdate(BaseModel):
    """Model for updating an existing project.

    Only provides optional fields so partial updates are allowed.
    """

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Project Name"
    )
    description: str | None = Field(None, description="Project Description")

    model_config = ConfigDict(from_attributes=True)


class ProjectResponse(ProjectBase):
    """Response model containing project metadata returned to clients."""

    id: int = Field(..., description="Project ID")
    created_at: datetime = Field(..., description="Project Creation Date and Time")
    updated_at: datetime | None = Field(
        ..., description="Project Updating Date and Time"
    )
