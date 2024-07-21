from os import getenv
from typing import Literal

from beanie.odm.operators.update.general import Set
from fastapi import APIRouter, HTTPException, Depends, Query, Response
from fastapi import status

from app.models import Response_Model
from app.models.user import User
from app.utils.user import get_admin_id
from app.utils.pagination import paginate


api = APIRouter()


@api.get('/', response_model=Response_Model)
async def get_all_users(
    response: Response,
    uid: str = Depends(get_admin_id),
    page: int = Query(1, description='page number'),
    page_size: int = Query(10),
    sort: str = Query('id'),
    desc: bool = Query(False, description='sort descending'),
):
    """
    """
    try:
        page_data = await paginate(User, page, page_size, sort, desc)
        items = page_data['items']
        items = [i.get_profile()|i.get_details() for i in items]
        page_data['items'] = items
        data = {
            'success': True,
            'message': '',
            'data': page_data,
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.get('/{id}/', response_model=Response_Model)
async def get_user_by_id(
    response: Response,
    id: str,
    uid: str = Depends(get_admin_id),
):
    """
    """
    try:
        user = await User.get(id)
        data = {
            'success': True,
            'message': '',
            'data': user.get_profile() | user.get_details(),
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.patch('/activate/{id}/', response_model=Response_Model)
async def active_or_deactive_a_user(
    response: Response,
    id: str,
    uid: str = Depends(get_admin_id),
):
    """
    """
    try:
        user = await User.get(id)
        match user.is_user_active:
            case True: verb = 'deactivated'
            case False: verb = 'activated'
        user.is_user_active = not user.is_user_active
        await user.save()
        #
        data = {
            'success': True,
            'message': f'User has been {verb} successfully.',
            'data': {'is_user_active': user.is_user_active},
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data