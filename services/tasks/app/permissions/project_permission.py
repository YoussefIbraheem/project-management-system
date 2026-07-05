from shared.exceptions import BadRequestException, ForbiddenException
from app.validators.project_validator import get_member_or_404

from app.models import Project
from app.security.actor import Actor
from app.security.roles import MemberRole, get_role_object, has_power


def can_view_projects(db, actor: Actor):
    return True


def can_view_project(db, actor: Actor):
    return True


def can_create_project(db, actor: Actor):
    return True


def can_update_project(db, actor: Actor, project: Project):
    if actor.can_override():
        return

    member = get_member_or_404(db, project.id, actor.user_id) #type: ignore
    role = get_role_object(member.role)

    if not has_power(role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_delete_project(db, actor: Actor, project: Project):
    if actor.can_override():
        return

    member = get_member_or_404(db, project.id, actor.user_id) #type: ignore
    role = get_role_object(member.role)

    if not has_power(role, MemberRole.OWNER):
        raise ForbiddenException()


def can_view_project_members(db, actor: Actor, project: Project):
    if actor.can_override():
        return

    member = get_member_or_404(db, project.id, actor.user_id) #type: ignore
    role = get_role_object(member.role)

    if not has_power(role, MemberRole.MEMBER):
        raise ForbiddenException()

def can_view_project_member(db, actor: Actor, project: Project):
    if actor.can_override():
        return

    member = get_member_or_404(db, project.id, actor.user_id) #type: ignore
    role = get_role_object(member.role)

    if not has_power(role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_create_project_member(db, actor: Actor, project: Project):
    if actor.can_override():
        return

    member = get_member_or_404(db, project.id, actor.user_id) #type: ignore
    role = get_role_object(member.role)

    if not has_power(role, MemberRole.OWNER):
        raise ForbiddenException()


def can_update_project_member_role(db, actor: Actor, project, target_user_id):
    if actor.can_override():
        return

    action_member = get_member_or_404(db, project.id, actor.user_id)
    action_member_role = get_role_object(action_member.role)

    target_member = get_member_or_404(db, project.id, target_user_id)

    if not has_power(
        action_member_role, MemberRole.OWNER
    ):  # cannot change role of non-manager
        raise ForbiddenException()

    if action_member.user_id == target_member.user_id: #type: ignore
        raise BadRequestException()


def can_delete_project_member(db, actor: Actor, project, target_user_id):
    if actor.can_override():
        return

    action_member = get_member_or_404(db, project.id, actor.user_id)
    action_member_role = get_role_object(action_member.role)
    target_member = get_member_or_404(db, project.id, target_user_id)

    if not has_power(
        action_member_role, MemberRole.OWNER
    ):  # cannot delete member of non-manager project
        raise ForbiddenException()

    if action_member.user_id == target_member.user_id: #type: ignore
        raise BadRequestException()
