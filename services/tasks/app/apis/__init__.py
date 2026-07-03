from flask_jwt_extended import get_jwt, get_jwt_identity

from app.security.actor import Actor


def get_actor() -> Actor:

    claims = get_jwt()
    user_id = str(get_jwt_identity())
    actor = Actor(
        user_id=user_id,
        is_superuser=claims.get("is_superuser", False),
    )
    return actor
