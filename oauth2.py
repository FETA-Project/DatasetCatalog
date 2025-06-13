from datetime import datetime
from fastapi import HTTPException, Request

from models import User

from config import config


async def require_admin(request: Request):
    return await _require_user(request, True)


async def require_user(request: Request):
    return await _require_user(request, False)


async def _require_user(request: Request, require_admin: bool):
    if config.DEV:
        _user = await User.find(User.email == config.DEV_USER).first_or_none()
        assert _user is not None
        if require_admin:
            _user.check_admin()
        return _user

    user_id = request.headers.get("X-User-ID").encode("latin").decode("utf-8")
    user_name = request.headers.get("X-User-Name", "").encode("latin").decode("utf-8")
    user_sn = request.headers.get("X-User-Surname", "").encode("latin").decode("utf-8")

    user = await User.find(User.email == user_id).first_or_none()

    if not user:
        new_user = User(
            email=user_id, name=user_name, surname=user_sn, created_at=datetime.utcnow()
        )
        user = new_user
        print("Creating user", user.to_dict())
        await new_user.insert()
    else:
        print("Updating user", user.to_dict(), user_name, user_sn)
        if user_name != user.name or user_sn != user.surname:
            user.name = user_name
            user.surname = user_sn
            await user.save()

    if require_admin:
        user.check_admin()

    return user
