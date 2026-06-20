from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class BoardColumnBase(BaseModel):
    id: int = Field(..., description="Board Column ID")
    board_id: int = Field(..., description="Parent Board ID")
    slug: str = Field(..., min_length=1, max_length=50, description="Column Slug")
    label: str = Field(..., min_length=1, max_length=100, description="Column Label")
    status_group: str = Field(
        ...,
        description="Status Group (pending, in_progress, done, cancelled)",
    )

    model_config = ConfigDict(from_attributes=True)


class BoardColumnResponse(BoardColumnBase):
    """Class for responding with board column information. Inherits from BoardColumnBase and adds ID field."""

    pass


class BoardColumnCreate(BaseModel):
    """Class for creating a new board column."""

    board_id: int = Field(..., description="Parent Board ID")
    slug: str = Field(..., min_length=1, max_length=50, description="Column Slug")
    label: str = Field(..., min_length=1, max_length=100, description="Column Label")
    status_group: str = Field(
        ...,
        description="Status Group (pending, in_progress, done, cancelled)",
    )

    model_config = ConfigDict(from_attributes=True)


class BoardColumnUpdate(BaseModel):
    """Class for updating an existing board column. Only allows updating slug, label, and status_group."""

    slug: Optional[str] = Field(
        None, min_length=1, max_length=50, description="Column Slug"
    )
    label: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Column Label"
    )
    status_group: Optional[str] = Field(
        None,
        description="Status Group (pending, in_progress, done, cancelled)",
    )

    model_config = ConfigDict(from_attributes=True)
