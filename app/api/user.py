from os import getenv
from datetime import datetime

from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, Depends, Query, Response
from fastapi import status as Status

from app.models import Response_Model
from app.models.user import User


api = APIRouter()


@api.get('/', response_model=Response_Model)
async def get_all_users(
    response: Response,
    page: int = Query(1, description='page number'),
    page_size: int = Query(10),
    sort: str = Query('id'),
    desc: bool = Query(False, description='sort descending'),
    user_data: dict = Depends(...),
):
    """
    ...
    """
    try:
        #
        user = await User.get(user_data['uid'])

        #
        data = {
            'success': True,
            'message': '',
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

