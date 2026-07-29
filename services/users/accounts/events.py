import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone


@dataclass
class BaseEvent:
    actor_id: str
    subject_id: str
    subject_type: str = "users"
    service: str = "users"
    action: str = field(init=False)
    timestamp: str = field(init=False)
    metadata: dict | None = None

    def __post_init__(self):
        name = self.__class__.__name__.replace("Event", "")
        self.action = re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()
        self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class UserRegisterEvent(BaseEvent):
    def __init__(
        self,
        subject_id: str,
        email: str,
        username: str,
        actor_id: str,
        display_name: str | None = None,
    ):
        self.metadata = {
            "email": email,
            "username": username,
            "user_id": subject_id,
            "display_name": display_name,
        }

        super().__init__(
            subject_id=subject_id, actor_id=actor_id, metadata=self.metadata
        )


@dataclass
class UserLoginEvent(BaseEvent):
    def __init__(self, subject_id: str, email: str, actor_id: str, username: str):
        super().__init__(
            subject_id=subject_id,
            actor_id=actor_id,
            metadata={"email": email, "username": username},
        )


@dataclass
class UserLogoutEvent(BaseEvent):
    def __init__(self, subject_id: str, actor_id: str, email: str, username: str):
        super().__init__(
            subject_id=subject_id,
            actor_id=actor_id,
            metadata={"email": email, "username": username},
        )


@dataclass
class UserProfileUpdateEvent(BaseEvent):
    def __init__(
        self,
        subject_id: str,
        actor_id: str,
        email: str,
        username: str,
        updated_fields: list | None = [],
    ):
        super().__init__(
            subject_id=subject_id,
            subject_type="user_profile",
            actor_id=actor_id,
            metadata={
                "email": email,
                "username": username,
                "updated_fields": updated_fields,
            },
        )


@dataclass
class UserPasswordChangeEvent(BaseEvent):
    def __init__(
        self,
        subject_id: str,
        actor_id: str,
        change_source: str | None,
        auth_method: str | None,
        ip_address: str | None,
        user_agent: str | None,
        sessions_invalidated: bool = True,
    ):
        super().__init__(
            subject_id=subject_id,
            actor_id=actor_id,
            metadata={
                "change_source": change_source,
                "auth_method": auth_method,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "sessions_invalidated": sessions_invalidated,
            },
        )


@dataclass
class UserEmailChangeEvent(BaseEvent):
    def __init__(self, subject_id: str, new_email: str, actor_id: str):
        super().__init__(
            subject_id=subject_id, actor_id=actor_id, metadata={"new_email": new_email}
        )


@dataclass
class UserEmailVerificationSendEvent(BaseEvent):
    def __init__(self, subject_id: str, actor_id: str, code: str, email: str):
        super().__init__(
            subject_id=subject_id,
            actor_id=actor_id,
            metadata={"code": code, "email": email},
        )


@dataclass
class UserDeleteEvent(BaseEvent):
    def __init__(self, subject_id: str, email: str, actor_id: str):
        super().__init__(
            subject_id=subject_id, actor_id=actor_id, metadata={"email": email}
        )
