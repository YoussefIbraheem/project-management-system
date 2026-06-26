from app.core.flask_enum import FlaskEnum


class MemberRole(FlaskEnum):
    OWNER = "owner", "Owner"
    MANAGER = "manager", "Manager"
    MEMBER = "member", "Member"


ROLE_POWER = {
    MemberRole.MEMBER: 1,
    MemberRole.MANAGER: 2,
    MemberRole.OWNER: 3,
}


def has_role_at_least(role: MemberRole, minimum: MemberRole) -> bool:
    return ROLE_POWER[role] >= ROLE_POWER[minimum]
