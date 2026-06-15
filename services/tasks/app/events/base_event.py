import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class BaseEvent:
    actor_id: str
    subject_id: str
    subject_type: str
    service: str = "tasks"
    action: str = field(init=False)
    timestamp: str = field(init=False)
    metadata: Optional[dict] = None

    def __post_init__(self):
        name = self.__class__.__name__.replace("Event", "")
        self.action = re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()
        self.timestamp = datetime.now(timezone.utc).isoformat()
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        return asdict(self)
