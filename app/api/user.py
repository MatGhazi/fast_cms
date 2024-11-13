from datetime import datetime
from pytz import UTC

from bcrypt import hashpw, gensalt, checkpw
from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends, File, Response, Request, status, UploadFile

from app.models import Response_Model
from app.models.user import User, Deletion_Request
from app.models.user import Username, Join, Login, Profile, Usemo, Password, Delete_Me
from app.utils.image import upload as upload_image
from app.utils.image import delete as delete_image
from app.utils.user import create_token, get_user_id, send_otp, check_otp
from app.texts import get_deletion_reasons
import app.settings as settings
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse


api = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@api.post('/available/', response_model=Response_Model)
async def check_if_username_is_available(
    response: Response,
    request: Username,
):
    """
    """
    try:
        data = {
            'success': True,
            'message': 'The username is available.',
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
        hashed_password = hashpw(user_data['password'].encode('utf-8'), gensalt(rounds=settings.HASHING_COST))
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
        hashed_token = hashpw(token.encode('utf-8'), gensalt(rounds=settings.HASHING_COST)).decode('utf-8')
        user.tokens.append(hashed_token)
        await user.save()
        #
        response.status_code = status.HTTP_200_OK
        data = {
            'success': True,
            'message': 'You have been registered successfully.',
            'data': {'token': token},
        }
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data

@api.get("/signin/", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("sign_in.html", {"request": request})

@api.get("/signup/", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("sign_up.html", {"request": request})

@api.get("/reset-password/", response_class=HTMLResponse)
async def reset_password_page(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request})

@api.get("/flashcards/")
async def flashcard_endpoint():
    return {"message": "Successful"}
   

@api.post('/login/', response_model=Response_Model)
async def login(
    response: Response,
    request: Login,
):
    """
    """
    try:
        if request.usemo.startswith('+'):
            field = 'mobile'
        elif '@' in request.usemo:
            field = 'email'
        else:
            field = 'username'
        #
        user = await User.find_one({field: request.usemo})
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
        if not checkpw(request.password.encode('utf-8'), user.password.encode('utf-8')):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect credentials')
        #
        token = create_token(user.id)
        hashed_token = hashpw(token.encode('utf-8'), gensalt(rounds=settings.HASHING_COST)).decode('utf-8')
        tokens = user.tokens
        tokens.append(hashed_token)
        if len(tokens) > settings.MAX_SESSION_COUNT:
            tokens.pop(0)
        user.tokens = tokens
        await user.save()
        #
        deletion_request = await Deletion_Request.find_one({'uid':str(user.id)})
        if deletion_request:
            await deletion_request.delete()
            deletion_canceled = True
        else:
            deletion_canceled = False
        #
        data = {
            'success': True,
            'message': 'You are logged in successfully.',
            'data': {
                'token': token,
                'deletion_canceled': deletion_canceled,
            },
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
    uid: str = Depends(get_user_id),
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


# @api.put('/avatar/', response_model=Response_Model)
# async def update_avatar(
#     response: Response,
#     uid: str = Depends(get_user_id),
#     file: UploadFile = File(...),
# ):
#     """
#     """
#     try:
#         user = await User.get(uid)
#         if user.avatar:
#             await delete_image(user.avatar, uid)
#         #
#         image_id = await upload_image(
#             uid=uid, 
#             model='User', 
#             object_id=uid, 
#             field='avatar', 
#             file=file,
#             settings=settings.AVATAR,
#         )
#         user.avatar = image_id
#         await user.save()
#         #
#         data = {
#             'success': True,
#             'message': 'Your avatar has been updated.',
#             'data': {'image_id': image_id},
#         }
#         response.status_code = status.HTTP_200_OK
#     except HTTPException as e:
#         data = {'success': False, 'message': e.detail, 'data': None}
#         response.status_code = e.status_code
#     except Exception as e:
#         data = {'success': False, 'message': str(e), 'data': None}
#         response.status_code = status.HTTP_406_NOT_ACCEPTABLE
#     return data


@api.delete('/avatar/', response_model=Response_Model)
async def delete_avatar(
    response: Response,
    uid: str = Depends(get_user_id),
):
    """
    """
    try:
        user = await User.get(uid)
        if not user.avatar:
            raise Exception('You do NOT have any avatar to delete!')
        # 
        await delete_image(user.avatar, uid)
        user.avatar = None
        await user.save()
        #
        data = {
            'success': True,
            'message': 'Your avatar has been deleted.',
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
async def request_for_an_otp(
    request: Usemo,
    response: Response,
    background_tasks: BackgroundTasks
):
    """
    """
    try:
        if request.usemo.startswith('+'):
            field = 'mobile'
        elif '@' in request.usemo:
            field = 'email'
        else:
            field = 'username'
        #
        user = await User.find_one({field: request.usemo})
        if not user:
            raise Exception('User not found!')
        #
        await send_otp(user, background_tasks)
        #
        data = {
            'success': True,
            'message': 'An OTP was sent!',
            'data': None
        }
        response.status_code = status.HTTP_200_OK
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.put('/password/', response_model=Response_Model)
async def reset_password(
    request: Password, 
    response: Response,
):
    """
    """
    try:
        if request.usemo.startswith('+'):
            field = 'mobile'
        elif '@' in request.usemo:
            field = 'email'
        else:
            field = 'username'
        #
        user = await User.find_one({field: request.usemo})
        if not user:
            raise Exception('User not found!')
        #
        check_otp(user, request.otp)
        #
        user.password = hashpw(request.password.encode('utf-8'), gensalt(rounds=settings.HASHING_COST)).decode('utf-8')
        user.otp = None
        user.otp_datetime = None
        await user.save()
        #
        response.status_code = status.HTTP_200_OK
        data = {
            'success': True,
            'message': 'Password has been updated.',
            'data': None,
        }
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.get('/reasons/', response_model=Response_Model)
async def get_delete_account_reasons(
    response: Response,
    uid: str = Depends(get_user_id),
):
    """
    """
    try:
        #
        response.status_code = status.HTTP_200_OK
        data = {
            'success': True,
            'message': '',
            'data': get_deletion_reasons(),
        }
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.post('/deleteme/', response_model=Response_Model)
async def delete_me(
    response: Response,
    request: Delete_Me,
    uid: str = Depends(get_user_id),
):
    """
    Right to be forgotten

    A predefined reason or custom reason that starts with the character "+"
    """
    try:
        await Deletion_Request(
            uid=uid,
            datetime=datetime.now(UTC),
            is_deleted=False,
            reason=request.reason,
        ).create()
        #
        user = await User.get(uid)
        user.tokens = []
        await user.save()
        # 
        response.status_code = status.HTTP_200_OK
        data = {
            'success': True,
            'message': f'Your deletion request has been submitted. Your account will be deleted within {settings.DELETION_BREAK_IN_DAYS} days.',
            'data': None,
        }
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data

