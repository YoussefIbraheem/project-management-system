from pydantic import BaseModel, ConfigDict, Field


class ProjectMemberBase(BaseModel):
    project_id: int = Field(..., gt=0, ,alias="proejctId")
    user_id: int = Field(..., gt=0, alias="userId")
    role_id: int = Field(..., gt=0, alias="roleId")

    model_config = ConfigDict(from_attributes=True)

class ProjectMemberCreate(ProjectMemberBase):
    pass


class ProjectMemberResponse(ProjectMemberBase):
    project_id: int = Field(..., alias="proejctId")
    user_id: int = Field(..., alias="userId")
    role_id: int = Field(..., alias="roleId")


class ProjectMemberUpdate(BaseModel):
    role_id: int = Field(..., alias="roleId")

    model_config = ConfigDict(from_attributes=True)
