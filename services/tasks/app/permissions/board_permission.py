from shared.exceptions import ForbiddenException
from app.models import Board
from app.security.roles import MemberRole, get_role_object, has_power
from app.validators.project_validator import get_member_or_404


def can_view_boards(db, actor, project_id):
    if actor.can_override():
        return

    member = get_member_or_404(db, project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_view_board(db, actor, project_id):
    if actor.can_override():
        return

    member = get_member_or_404(db, project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_create_board(db, actor, project_id):
    if actor.can_override():
        return

    member = get_member_or_404(db, project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_update_board(db, actor, target_board: Board):
    if actor.can_override():
        return

    member = get_member_or_404(db, target_board.project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_delete_board(db, actor, target_board: Board):
    if actor.can_override():
        return

    member = get_member_or_404(db, target_board.project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_view_board_columns(db, actor, target_board: Board):
    if actor.can_override():
        return

    member = get_member_or_404(db, target_board.project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_view_board_column(db, actor, target_board: Board):
    if actor.can_override():
        return

    member = get_member_or_404(db, target_board.project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MEMBER):
        raise ForbiddenException()


def can_create_board_column(db, actor, target_board: Board):
    if actor.can_override():
        return

    member = get_member_or_404(db, target_board.project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_update_board_column(db, actor, target_board: Board):
    if actor.can_override():
        return

    member = get_member_or_404(db, target_board.project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()


def can_delete_board_column(db, actor, target_board: Board):
    if actor.can_override():
        return

    member = get_member_or_404(db, target_board.project_id, actor.user_id)
    member_role = get_role_object(member.role)

    if not has_power(member_role, MemberRole.MANAGER):
        raise ForbiddenException()