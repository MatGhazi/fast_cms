from os import getenv
from datetime import datetime

from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, Query, Response
from fastapi import status as Status

from app.components.user import check_admin, check_user
from app.models import Response_Model
from app.models.user import User, Register, Login, Profile


api = APIRouter()


"""
@api.get('/available/{username}/', response_model=Response_Model)
@api.get('/check/{via}/{value}/', response_model=Response_Model)
@api.get('/me/', response_model=Response_Model)
@api.get('/{id}/', response_model=Response_Model)
@api.post('/register/', response_model=Response_Model)
@api.put('/avatar/', response_model=Response_Model)
@api.post('/otp/', response_model=Response_Model)
@api.post('/login/', response_model=Response_Model)
@api.delete('/logout/', response_model=Response_Model)
@api.put('/password/', response_model=Response_Model)

"""

@api.get('/', response_model=Response_Model)
async def get_all_users(
    response: Response,
    user_data: dict = Depends(check_admin),
    page: int = Query(1, description='page number'),
    page_size: int = Query(10),
    sort: str = Query('id'),
    desc: bool = Query(False, description='sort descending'),
):
    """
    ...
    """
    try:
        #
        users = await User.find().to_list()
        data = {
            'success': True,
            'message': '',
            'data': users,
        }
        response.status_code = Status.HTTP_200_OK
    except Exception as e:
        data = {
            'success': False, 
            'message': str(e), 
            'data': None
        }
        response.status_code = Status.HTTP_406_NOT_ACCEPTABLE
    return data



@api.post('/register/', response_model=Response_Model)
async def register(
    response: Response,
    request: Register,
):
    """
    """
    try:
        User(request.model_dump()).save()
        data = {
            'success': True,
            'message': 'You are registered successfully.',
            'data': None,
        }
        response.status_code = Status.HTTP_200_OK
    except Exception as e:
        data = {
            'success': False, 
            'message': str(e), 
            'data': None
        }
        response.status_code = Status.HTTP_406_NOT_ACCEPTABLE
    return data