import asyncio
from functools import wraps
import sys
import tempfile
import threading
from typing import Any

from fastapi.responses import JSONResponse


def disabled(
    status_code: int = 405,
    content: str = "Sorry, function is not enabled at this time.",
):
    def decorator(func):
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> JSONResponse:
            return JSONResponse(status_code=status_code, content=content)

        return wrapper

    return decorator


class ProgressPercentage(object):
    def __init__(self, filename: str, size: float):
        self._filename = filename
        self._size = size
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s %s / %s  (%.2f%%)"
                % (self._filename, self._seen_so_far, self._size, percentage)
            )
            sys.stdout.flush()

    def percentage(self):
        with self._lock:
            return (self._seen_so_far / self._size) * 100
