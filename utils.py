from functools import wraps
from typing import Any

from fastapi.responses import JSONResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def disabled(status_code: int = 405, content: str = 'Sorry, function is not enabled at this time.'):
    def decorator(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
            return JSONResponse(status_code=status_code, content=content)

        return wrapper

    return decorator


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)
