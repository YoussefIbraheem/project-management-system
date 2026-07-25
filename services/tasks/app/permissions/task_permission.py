from shared.exceptions import BadRequestException, ForbiddenException

from app.models import Task
from app.permissions.project_permission import get_member_or_404
from app.security.actor import Actor
from app.security.roles import MemberRole, get_role_object, has_power


def can_view_tasks(db, actor: Actor, project_id: int):
    if actor.can_override():
        return
    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_view_task(db, actor: Actor, project_id: int):
    if actor.can_override():
        return
    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_create_task(db, actor: Actor, project_id: int):
    if actor.can_override():
        return

    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_update_task(db, actor: Actor, project_id: int):
    if actor.can_override():
        return

    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_delete_task(db, actor: Actor, project_id: int, target_task: Task):
    if actor.can_override():
        return

    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()

    if actor.user_id != target_task.creator_id:
        raise ForbiddenException()


def can_view_task_assignees(db, actor: Actor, project_id: int):
    if actor.can_override():
        return

    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_view_task_assignee(db, actor: Actor, project_id: int):
    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_create_task_assignee(
    db, actor: Actor, project_id: int, target_task: Task, target_member_user_id: str
):
    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()

    if actor.user_id != target_task.creator_id:
        raise ForbiddenException()

    target_member = get_member_or_404(db, project_id, target_member_user_id)

    if not target_member:
        raise BadRequestException(
            message="Target member is not part of the project or does not exist"
        )


def can_update_task_assignee(
    db, actor: Actor, project_id: int, target_member_user_id: str, target_task: Task
):
    pass


def can_delete_task_assignee(
    db, actor: Actor, project_id: int, target_task: Task, target_member_user_id: str
):
    member = get_member_or_404(db, project_id, actor.user_id)
    if not member:
        raise ForbiddenException()

    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()

    if actor.user_id != target_task.creator_id:
        raise ForbiddenException()

    target_member = get_member_or_404(db, project_id, target_member_user_id)

    if not target_member:
        raise BadRequestException(
            message="Target member is not part of the project or does not exist"
        )
