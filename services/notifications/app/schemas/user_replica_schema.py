from typing import Optional

from pydantic import BaseModel, Field


class UserReplicaCreate(BaseModel):
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address of the user")
    username: str = Field(..., description="Username of the user")
    displayname: Optional[str] = Field(None, description="Display name of the user")
