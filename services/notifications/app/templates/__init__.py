from dataclasses import dataclass
from typing import Optional


@dataclass
class NotificationContent:
    title: str
    body: str
    email_subject: Optional[str]
    email_body: str