import time
from typing import Dict

import jwt

from app.core.config import settings


def token_response(token: str):
    return {"access_token": token}


def decode_jwt(token: str) -> dict | None:
    try:
        decoded_token = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except jwt.ExpiredSignatureError as e:
        return {"error": "Token expired"}
    except Exception as e:
        print(e)
        return {"error": "Invalid token"}
