from dataclasses import dataclass


@dataclass
class NotificationContent:
    subject: str
    body: str
    recipient_email: str
    notification_id: int | None = None


@dataclass
class BaseNotificationContext:
    recipient_email: str
    username: str
    actor_username: str


@dataclass
class TaskNotificationContext(BaseNotificationContext):
    task_title: str
    project_name: str


@dataclass
class ProjectNotificationContext(BaseNotificationContext):
    project_name: str


@dataclass
class TaskStatusNotificationContext(TaskNotificationContext):
    current_column: str
    new_column: str
