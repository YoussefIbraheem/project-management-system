from dataclasses import dataclass
from typing import Optional

from app.models import Board, ProjectMember
from app.security.actor import Actor
from app.models.board_column import BoardColumn
from app.models.project import Project

from .roles import MemberRole


@dataclass
class ProjectPermissionContext:
    actor: Actor
    action_member: ProjectMember
    target_member: ProjectMember | None = None
    target_role: MemberRole | None = None


@dataclass
class BoardPermissionContext:
    actor: Actor
    action_member: ProjectMember
    target_project_id: int
    target_board: Board | None = None
    target_column: BoardColumn | None = None
