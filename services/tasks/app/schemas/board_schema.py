from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from .board_column_schema import BoardColumnResponse


class BoardBase(BaseModel):
    id: int = Field(..., description="Board ID")
    name: str = Field(..., min_length=1, max_length=255, description="Board Name")
    description: str | None = Field(None, description="Board Description")
    project_id: int = Field(..., description="Parent Project")
    columns: list[BoardColumnResponse] | None = Field([], description="Board Columns")
    created_at: datetime = Field(..., description="Board Creation Date and Time")
    updated_at: datetime | None = Field(
        ..., description="Board Updating Date and Time"
    )

    model_config = ConfigDict(from_attributes=True)


class BoardResponse(BoardBase):
    """Class for responding with board information. Inherits from BoardBase and adds ID and timestamp fields."""



class BoardCreate(BaseModel):
    """Class for creating a new board. Inherits from BoardBase and does not add any new fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Board Name")
    description: str | None = Field(None, description="Board Description")
    project_id: int = Field(..., description="Parent Project")
    default_columns: bool = Field(
        default=True,
        description="When creating a new board, whether to add default columns or not.",
    )

    model_config = ConfigDict(from_attributes=True)


class BoardUpdate(BaseModel):
    """Class for updating an existing board. Only allows updating name, description, and columns."""

    name: str | None = Field(
        None, min_length=1, max_length=255, description="Board Name"
    )
    description: str | None = Field(None, description="Board Description")

    model_config = ConfigDict(from_attributes=True)
