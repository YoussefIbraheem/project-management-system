import logging
import time

import jwt

from app.core.config import settings

logger = logging.getLogger(__name__)


def token_response(token: str):
    return {"access_token": token}


def decode_jwt(token: str) -> dict | None:
    try:
        logger.info(f"TOKEN:{token}")
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM] #type: ignore
        )
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except jwt.ExpiredSignatureError as e:
        logger.error(f"Token expired: {e}")
        raise ValueError("Token has expired") from e
    except Exception as e:
        logger.error(f"Error decoding JWT: {e}")
        raise ValueError("Invalid token") from e
