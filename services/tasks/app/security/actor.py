from dataclasses import dataclass


@dataclass(frozen=True)
class Actor:
    user_id: str
    is_superuser: bool = False

    def can_override(self):
        return self.is_superuser
