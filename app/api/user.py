from datetime import datetime, UTC
from os import getenv

from bcrypt import hashpw, gensalt, checkpw
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, HTTPException, Depends, Response, Request
from fastapi import status

from app.models import Response_Model
from app.models.user import User, Username, Join, Login, Profile, Avatar
from app.utils.user import create_token, get_user_id


api = APIRouter()


@api.post('/available/', response_model=Response_Model)
async def check_if_username_is_available(
    response: Response,
    request: Username,
):
    """
    """
    try:
        user = await User.find_one(User.username == request.username)
        if user:
            availablity = False
            message = 'Sorry! The username is taken.'
        else:
            availablity = True
            message = 'The username is available.'
        #
        data = {
            'success': True,
            'message': message,
            'data': {'availablity': availablity},
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.post('/join/', response_model=Response_Model)
async def join(
    response: Response,
    request: Join,
):
    """
    Some documents ...
    """
    try:
        user_data = request.model_dump()
        hashed_password = hashpw(user_data['password'].encode('utf-8'), gensalt())
        user_data['password'] = hashed_password.decode('utf-8')
        user_data['registration_datetime'] = datetime.now(UTC)
        user_data['is_user_active'] = True
        user_data['is_admin'] = False
        user = User(**user_data)
        await user.create()
        #
        # TODO: Verify email / mobile
        #
        token = create_token(user.id)
        hashed_token = hashpw(token.encode('utf-8'), gensalt()).decode('utf-8')
        user.tokens.append(hashed_token)
        await user.save()
        #
        data = {
            'success': True,
            'message': 'You have been registered successfully.',
            'data': {'token': token},
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.post('/login/', response_model=Response_Model)
async def login(
    response: Response,
    request: Login,
):
    """
    """
    #
    # TODO: Check if the user has already been signed in 
    #
    try:
        user = await User.find_one(User.username == request.usemo)
        if not user:
            user = await User.find_one(User.email == request.usemo)
        if not user:
            user = await User.find_one(User.mobile == request.usemo)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
        if not checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
        #
        token = create_token(user.id)
        hashed_token = hashpw(token.encode('utf-8'), gensalt()).decode('utf-8')
        tokens = user.tokens
        tokens.append(hashed_token)
        if len(tokens) > int(getenv('MAX_SESSION_COUNT')):
            tokens.pop(0)
        user.tokens = tokens
        await user.save()
        #
        data = {
            'success': True,
            'message': 'You are logged in successfully.',
            'data': {'token': token},
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_400_BAD_REQUEST
    return data


@api.delete('/logout/', response_model=Response_Model)
async def logout(
    response: Response,
    request: Request,
    uid: dict = Depends(get_user_id),
):
    """
    """
    try:
        #
        authorization = request.headers.get('Authorization')
        token = authorization.split()[-1]
        user = await User.get(uid)
        #
        for t in user.tokens:
            if checkpw(token.encode('utf-8'), t.encode('utf-8')):
                user.tokens.remove(t)
                await user.save()
        #
        response.status_code = status.HTTP_200_OK
        data = {
            'success': True,
            'message': 'You are logged out successfully.',
            'data': None,
        }
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.get('/profile/', response_model=Response_Model)
async def get_profile(
    response: Response,
    uid: str = Depends(get_user_id),
):
    """
    """
    try:
        user = await User.get(uid)
        data = {
            'success': True,
            'message': '',
            'data': user.get_profile(),
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.put('/profile/', response_model=Response_Model)
async def update_profile(
    response: Response,
    request: Profile,
    uid: str = Depends(get_user_id),
):
    """
    """
    try:
        user = await User.get(uid)
        await user.update(Set(request.model_dump()))
        data = {
            'success': True,
            'message': 'Your profile has been updated.',
            'data': None,
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.put('/avatar/', response_model=Response_Model)
async def update_avatar(
    response: Response,
    request: Avatar,
    uid: str = Depends(get_user_id),
):
    """
    """
    try:
        user = await User.get(uid)
        user.avatar = request.avatar
        await user.save()
        data = {
            'success': True,
            'message': 'Your avatar has been updated.',
            'data': None,
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.patch('/otp/', response_model=Response_Model)
async def request_for_an_otp():...


@api.put('/password/', response_model=Response_Model)
async def reset_password():...
