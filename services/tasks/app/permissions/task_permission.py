from security.roles import ROLE_POWER, MemberRole, get_role_object, has_power
from shared.exceptions import APIException, ForbiddenException

from app.security.context import TaskPermissionContext


def can_view_tasks(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_view_task(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_create_task(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_update_task(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_delete_task(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_view_task_assignees(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_view_task_assignee(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_create_task_assignee(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_update_task_assignee(ctx: TaskPermissionContext):
    pass


def can_delete_task_assignee(ctx: TaskPermissionContext):
    if ctx.actor.can_override():
        return

    task_project_id =  int(ctx.target_project_id)
    member_project_id = int(ctx.action_member.project_id)
    if member_project_id != task_project_id:
        raise ForbiddenException()

    member_role = get_role_object(ctx.action_member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()
