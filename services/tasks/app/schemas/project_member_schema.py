from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ProjectMemberBase(BaseModel):
    project_id: int = Field(..., gt=0)
    user_id: str = Field(...)
    role: str = Field(...)

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberCreate(BaseModel):
    user_id: str = Field(...)
    role: Literal["owner", "manager", "member"] = Field(...)

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberUpdateRole(BaseModel):
    role: Literal["owner", "manager", "member"] = Field(...)

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(ProjectMemberBase):
    pass
