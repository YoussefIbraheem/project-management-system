from shared.exceptions import ForbiddenException

from app.models import ProjectMember
from app.security.actor import Actor
from app.security.roles import MemberRole, get_role_object, has_power
from app.security.context import ProjectPermissionContext

def can_update_project(actor: Actor, member: ProjectMember):
    if actor.can_override():
        return

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("You don't have permission to update this project.")


def can_delete_project(actor: Actor, member: ProjectMember):
    if actor.can_override():
        return

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.OWNER):
        raise ForbiddenException("You don't have permission to update this project.")


def can_create_project_member(
    ctx:ProjectPermissionContext
):
    if ctx.actor.can_override():
        return

    action_member_role = get_role_object(ctx.action_member.role)

    if not has_power(action_member_role, ctx.target_role):
        raise ForbiddenException("You don't have permission to update this project.")


def can_update_project_member_role(
    ctx:ProjectPermissionContext
):
    if actor.can_override():
        return

    action_member_role = get_role_object(action_member.role)

    if not has_power(action_member_role, action_role):
        raise ForbiddenException("You don't have permission to update this project.")


def can_delete_project_member(
    ctx:ProjectPermissionContext
):
    if actor.can_override():
        return

    action_member_role = get_role_object(action_member.role)

    if not has_power(action_member_role, target_role):
        raise ForbiddenException("You don't have permission to update this project.")
