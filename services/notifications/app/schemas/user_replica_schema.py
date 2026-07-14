from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserReplicaSchema(BaseModel):
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address of the user")
    username: str = Field(..., description="Username of the user")
    display_name: Optional[str] = Field(None, description="Display name of the user")

    model_config = ConfigDict(from_attributes=True)


class UserReplicaCreateSchema(UserReplicaSchema):
    pass


class UserReplicaUpdateSchema(BaseModel):
    email: Optional[str] = Field(None, description="Email address of the user")
    username: Optional[str] = Field(None, description="Username of the user")
    displayname: Optional[str] = Field(None, description="Display name of the user")

    model_config = ConfigDict(from_attributes=True)
