from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime

class BoardBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Board Name")
    description: Optional[str] = Field(None, description="Board Description")
    project_id: int = Field(..., description="Parent Project")
    columns: list = Field(..., description="Board Columns")

    model_config = ConfigDict(from_attributes=True)


class BoardCreate(BoardBase):
    """Class for creating a new board. Inherits from BoardBase and does not add any new fields."""

    pass


class BoardUpdate(BaseModel):
    """Class for updating an existing board. Only allows updating name, description, and columns."""

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Board Name"
    )
    description: Optional[str] = Field(None, description="Board Description")
    columns: Optional[List[str]] = Field(None, description="Board Columns")

    model_config = ConfigDict(from_attributes=True)


class BoardResponse(BoardBase):
    """Class for responding with board information. Inherits from BoardBase and adds ID and timestamp fields."""

    id: int = Field(..., description="Board ID")
    created_at: datetime = Field(..., description="Board Creation Date and Time")
    updated_at: Optional[datetime] = Field(
        ..., description="Board Updating Date and Time"
    )
