from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Form, HTTPException, Response
from pymongo.errors import DuplicateKeyError

from config import config
from models import User
from oauth2 import AuthJWT, require_user

auth = APIRouter(prefix="/auth")

@auth.post('/register')
async def register(email: str = Form(...), name: str = Form(...), surname: str = Form(...), password: str = Form(...)):
    user = await User.find(User.email == email).first_or_none()
    print(user)

    if user:
        raise HTTPException(status_code=401,
                            detail='Account already exist')

    try:
        new_user = User(
            email=email,
            name=name,
            surname=surname,
            created_at=datetime.utcnow()
        )
        new_user.set_password(password)
        await new_user.insert()
    except DuplicateKeyError:
        raise HTTPException(
        status_code=401,
        detail=f"User with email '{email}' exists"
    )

    return {"status": "success", "user": new_user}


@auth.post('/login')
async def login(email: str = Form(...), password: str = Form(...), response: Response = Response, Authorize: AuthJWT = Depends()):
    user = await User.find(User.email == email).first_or_none()

    if not user:
        raise HTTPException(status_code=400, detail='Incorrect Email or Password')

    if not user.verify_password(password):
        raise HTTPException(status_code=400, detail='Incorrect Email or Password')

        # Create access token
    access_token = Authorize.create_access_token(
        subject=str(user.email), expires_time=timedelta(minutes=config.ACCESS_TOKEN_EXPIRES_IN))

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(user.email), expires_time=timedelta(minutes=config.REFRESH_TOKEN_EXPIRES_IN))

    # Store refresh and access tokens in cookie
    response.set_cookie('access_token', access_token, config.ACCESS_TOKEN_EXPIRES_IN * 60,
                        config.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token,
                        config.REFRESH_TOKEN_EXPIRES_IN * 60, config.REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', config.ACCESS_TOKEN_EXPIRES_IN * 60,
                        config.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    # Send both access
    return {'status': 'success', 'access_token': access_token}

@auth.get('/refresh')
async def refresh_token(response: Response, Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_refresh_token_required()

        user_email = Authorize.get_jwt_subject()
        if not user_email:
            raise HTTPException(status_code=401,
                                detail='Could not refresh access token')

        user = await User.find(User.email == user_email).first_or_none
        if not user:
            raise HTTPException(status_code=401,
                                detail='The user belonging to this token no logger exist')
        access_token = Authorize.create_access_token(
            subject=str(user.email), expires_time=timedelta(minutes=config.ACCESS_TOKEN_EXPIRES_IN))
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=400, detail='Please provide refresh token')
        raise HTTPException(
            status_code=400, detail=error)

    response.set_cookie('access_token', access_token, config.ACCESS_TOKEN_EXPIRES_IN * 60,
                        config.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', config.ACCESS_TOKEN_EXPIRES_IN * 60,
                        config.ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')
    return {'access_token': access_token}


@auth.get('/logout')
async def logout(response: Response, Authorize: AuthJWT = Depends(), user_email: str = Depends(require_user)):
    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}

