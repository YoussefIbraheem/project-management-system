from utils.exceptions import ForbiddenException
from app.security.actor import Actor
from app.security.roles import MemberRole, get_role, has_power
from app.models import ProjectMember


def can_update_project(actor: Actor, member: ProjectMember):
    if actor.can_override():
        return

    member_role = get_role(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("You don't have permission to update this project.")




def can_delete_project(actor: Actor, member: ProjectMember):
    if actor.can_override():
        return

    member_role = get_role(member.role)

    if not has_power(member_role, MemberRole.OWNER):
        raise ForbiddenException("You don't have permission to update this project.")




def can_create_project_member(actor: Actor, member: ProjectMember):
    if actor.can_override():
        return

    member_role = get_role(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("You don't have permission to update this project.")




def can_update_project_member_role(
    actor: Actor, member: ProjectMember
):
    if actor.can_override():
        return

    member_role = get_role(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("You don't have permission to update this project.")




def can_delete_project_member(actor: Actor, member: ProjectMember):
    if actor.can_override():
        return

    member_role = get_role(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("You don't have permission to update this project.")


