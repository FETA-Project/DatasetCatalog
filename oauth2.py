
import base64
from typing import List
from fastapi import Depends, HTTPException
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel

from models import User

from config import config

class Config(BaseModel):
    authjwt_algorithm: str = config.JWT_ALGORITHM
    authjwt_decode_algorithms: List[str] = [config.JWT_ALGORITHM]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = base64.b64decode(
        config.JWT_PUBLIC_KEY).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(
        config.JWT_PRIVATE_KEY).decode('utf-8')


@AuthJWT.load_config
def get_config():
    return Config()


class UserNotFound(Exception):
    pass

class UserNotAdmin(Exception):
    pass

async def require_admin(Authorize: AuthJWT = Depends()):
    return await _require_user(Authorize, True)

async def require_user(Authorize: AuthJWT = Depends()):
    return await _require_user(Authorize, False)

async def _require_user(Authorize: AuthJWT, require_admin: bool):
    try:
        Authorize.jwt_required()
        user_email = Authorize.get_jwt_subject()
        
        user = await User.find(User.email == user_email).first_or_none()

        if not user:
            raise UserNotFound('User no longer exist')

        if require_admin and not user.is_admin:
            raise UserNotAdmin('Please verify your account')

    except Exception as e:
        error = e.__class__.__name__
        print(error)
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=401, detail='You are not logged in')
        if error == 'UserNotFound':
            raise HTTPException(
                status_code=401, detail='User no longer exist')
        if error == 'UserNotAdmin':
            raise HTTPException(
                status_code=401, detail='This action requires admin')
        if error == 'NotVerified':
            raise HTTPException(
                status_code=401, detail='Please verify your account')
        raise HTTPException(
            status_code=401, detail='Token is invalid or has expired')
    return user_email
