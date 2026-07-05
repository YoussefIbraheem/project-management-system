from dataclasses import dataclass

from app.models import Board, BoardColumn, ProjectMember, Task, TaskAssignee
from app.security.actor import Actor

@dataclass
class TaskPermissionContext:
    actor: Actor
    action_member: ProjectMember
    target_project_id: int
    target_board: Board | None = None
    target_task: Task | None = None
    target_status: BoardColumn | None = None
    target_member: ProjectMember | None = None
    target_assignee: TaskAssignee | None = None
