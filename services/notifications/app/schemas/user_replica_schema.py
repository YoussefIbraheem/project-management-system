
from pydantic import BaseModel, ConfigDict, Field


class UserReplicaSchema(BaseModel):
    user_id: str = Field(..., description="User ID")
    email: str = Field(..., description="Email address of the user")
    username: str = Field(..., description="Username of the user")
    display_name: str | None = Field(None, description="Display name of the user")

    model_config = ConfigDict(from_attributes=True)
