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


def get_role(keyword) -> MemberRole:
    for role in MemberRole:
        if keyword == role.value or keyword.lower() == role.name.lower():
            return role
    raise ValueError(f"Invalid member role: {keyword}")


def has_power(member_role: MemberRole, role_allowed: MemberRole):
    return ROLE_POWER[member_role] >= ROLE_POWER[role_allowed]
    
        
    
