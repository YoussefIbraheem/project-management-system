from enum import StrEnum


class UserEventType(StrEnum):
    USER_REGISTER = "USER_REGISTER"
    USER_PROFILE_UPDATE = "USER_PROFILE_UPDATE"
    USER_DELETE = "USER_DELETE"