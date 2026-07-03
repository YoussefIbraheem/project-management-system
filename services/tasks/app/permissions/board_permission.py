from shared.exceptions import ForbiddenException

from app.security.context import BoardPermissionContext
from app.security.roles import MemberRole, get_role_object, has_power
from app import logger

def can_view_boards(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)
    logger.info(f"MEMBER PROJECT:{ctx.action_member.project_id}")
    logger.info(f"TARGET PROJECT:{ctx.target_project_id}")
    
    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Target user not member of the project")

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_view_board(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_create_board(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_update_board(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_delete_board(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_view_board_columns(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_view_board_column(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_create_board_column(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_update_board_column(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("Insufficient access power to perform action.")


def can_delete_board_column(ctx: BoardPermissionContext):
    if ctx.actor.can_override():
        return

    member_role = get_role_object(ctx.action_member.role)

    if int(ctx.action_member.project_id) != int(ctx.target_project_id):
        raise ForbiddenException("Insufficient access power to perform action.")

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException("Insufficient access power to perform action.")
