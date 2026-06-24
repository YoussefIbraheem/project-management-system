from pydantic import BaseModel, Field, ConfigDict

class MemberRoleCreate(BaseModel):
    label: str = Field(..., description="Role Label")
    slug: str = Field(..., description="Role Slug")

    model_config = ConfigDict(from_attributes=True)


class MemberRoleUpdate(MemberRoleCreate):
    pass


class MemberRoleResponse(MemberRoleCreate):
    id: int
    created_at: str
    updated_at: str
