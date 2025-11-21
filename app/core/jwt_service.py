from hashlib import sha256
import datetime as dt
from typing import Any, Dict

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from dotenv import load_dotenv
import os

load_dotenv()
secret = os.getenv("JWT_SECRET")

def hash_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()


class JWTError(Exception):
    """Общая ошибка JWT."""


def create_access_token(
    payload: Dict[str, Any],
    expires_in_seconds: int = 2700000,
    algorithm: str = "HS256",
) -> str:
    """
    Кодирует JWT с полем exp.
    """
    to_encode = payload.copy()
    now = dt.datetime.utcnow()
    exp = now + dt.timedelta(seconds=expires_in_seconds)
    to_encode["iat"] = now
    to_encode["exp"] = exp

    token = jwt.encode(to_encode, secret, algorithm=algorithm)
    # В PyJWT>=2 encode возвращает str
    return token


def decode_access_token(
    token: str,
    algorithms: list[str] | None = None,
    verify_exp: bool = True,
) -> Dict[str, Any]:
    """
    Декодирует и валидирует JWT.
    Бросает JWTError при любой проблеме.
    """
    if algorithms is None:
        algorithms = ["HS256"]

    options = {"verify_exp": verify_exp}

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=algorithms,
            options=options,
        )
        return payload
    except ExpiredSignatureError:
        raise JWTError("Токен истёк")
    except InvalidTokenError as e:
        raise JWTError(f"Неверный токен: {e}")
