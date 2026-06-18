from pydantic import BaseModel, ConfigDict, Field


class ProjectMemberBase(BaseModel):
    project_id: int = Field(..., gt=0)
    user_id: str = Field(...)
    role_id: int = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberCreate(BaseModel):
    user_id: str = Field(...)
    role_id: int = Field(..., gt=0)

    model_config = ConfigDict(from_attributes=True)


class ProjectMemberResponse(ProjectMemberBase):
    pass
