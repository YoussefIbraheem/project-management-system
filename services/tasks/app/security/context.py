from dataclasses import dataclass
from typing import Optional

from app.models.project_member import ProjectMember
from app.security.actor import Actor

from .roles import MemberRole


@dataclass
class ProjectPermissionContext:
    actor: Actor
    action_member: ProjectMember
    target_member: ProjectMember | None = None
    target_role: MemberRole | None = None
