from enum import StrEnum


class UserEventType(StrEnum):
    USER_REGISTER = "USER_REGISTER" # Creates a replica of a user when created
    USER_PROFILE_UPDATE = "USER_PROFILE_UPDATE" # Updates a replica of a user when profile is updated
    USER_DELETE = "USER_DELETE" # Deletes a replica of a user when deleted
    USER_LOGIN = "USER_LOGIN" #  Checks if a replica of this user exists