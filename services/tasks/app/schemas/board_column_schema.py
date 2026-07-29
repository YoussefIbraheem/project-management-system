from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BoardColumnBase(BaseModel):
    id: int = Field(..., description="Board Column ID")
    board_id: int = Field(..., description="Parent Board ID")
    slug: str = Field(..., min_length=1, max_length=50, description="Column Slug")
    label: str = Field(..., min_length=1, max_length=100, description="Column Label")
    status_group: str = Field(..., description="Status Group")

    model_config = ConfigDict(from_attributes=True)


class BoardColumnDetailsResponse(BoardColumnBase):
    """Class for responding with board column information. Inherits from BoardColumnBase and adds ID field."""



class BoardColumnResponse(BaseModel):
    id: int = Field(..., description="Board Column ID")
    label: str = Field(..., min_length=1, max_length=100, description="Column Label")

    model_config = ConfigDict(from_attributes=True)


class BoardColumnCreate(BaseModel):
    """Class for creating a new board column."""
    label: str = Field(..., min_length=1, max_length=100, description="Column Label")
    status_group: Literal["pending", "in_progress", "done", "cancelled"] = Field(
        default="pending",
        description="Status Group (pending, in_progress, done, cancelled)",
    )

    model_config = ConfigDict(from_attributes=True)


class BoardColumnUpdate(BaseModel):
    """Class for updating an existing board column. Only allows updating slug, label, and status_group."""

    slug: str | None = Field(
        None, min_length=1, max_length=50, description="Column Slug"
    )
    label: str | None = Field(
        None, min_length=1, max_length=100, description="Column Label"
    )
    status_group: str | None = Field(
        None,
        description="Status Group (pending, in_progress, done, cancelled)",
    )

    model_config = ConfigDict(from_attributes=True)
