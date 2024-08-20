from bson import ObjectId
from typing import Literal

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse

from app.models.media import Image
from app.models import Response_Model
from app.utils.pagination import paginate
from app.utils.image import upload, delete
from app.utils.user import get_user_id
import app.database as db
import app.settings as settings


api = APIRouter()


@api.post('/image/upload/', response_model=Response_Model)
async def upload_image(
    response: Response,
    uid: str = Depends(get_user_id),
    file: UploadFile = File(...),
    model: str = Form(...),
    field: str = Form(...),
    object_id: str = Form(...),
):
    """
    Try __NOT__ to use this method!
    
    use model specific methods instead, like `[PUT] /user/avatar/`
    """
    try:
        image_id = upload(
            uid=uid, 
            model=model, 
            object_id=object_id, 
            field=field, 
            file=file,
            settings=settings.IMAGE,
        ) 
        #
        data = {
            'success': True,
            'message': '',
            'data': {'image_id': image_id},
        }
        response.status_code = status.HTTP_200_OK
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.get('/image/', response_model=Response_Model)
async def get_all_images(
    response: Response,
    uid: str = Depends(get_user_id),
    mine: bool = Query(False),
    model: str = Query(None),
    object_id: str = Query(None),
    field: str = Query(None),
    page: int = Query(1, description='page number'),
    page_size: int = Query(10),
    sort: str = Query('id'),
    desc: bool = Query(False, description='sort descending'),
):
    """
    """
    try:
        filters = {
            'model':model, 
            'object_id':object_id, 
            'field':field
        }
        if mine:
            filters['uid'] = uid
        else:
            filters['is_public'] = True
        page_data = await paginate(Image, page, page_size, sort, desc, filters)
        #
        response.status_code = status.HTTP_200_OK
        data = {'success': True, 'message': '', 'data': page_data}
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.get('/image/{id}/{which}/')
async def get_image_by_id(
    response: Response,
    id: str,
    uid: str = Depends(get_user_id),
    which: str = Literal['full', 'thumbnail'],
):
    """
    """
    try:
        match which:
            case 'full': field = 'full_id'
            case 'thumbnail': field = 'thumbnail_id'
            case _: raise Exception('Wrong path!')
        #
        image = await Image.get(id)
        if not image:
            raise HTTPException(status_code=404, detail='Image not found')
        if not any([image.uid==uid, image.is_public]):
            raise Exception('Access denied!')
        #
        grid_out = await db.fs.open_download_stream(ObjectId(getattr(image, field)))
        #
        response.status_code = status.HTTP_200_OK
        data = StreamingResponse(grid_out, media_type=grid_out.metadata['content_type'])
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data


@api.delete('/image/{id}/', response_model=Response_Model)
async def delete_image(
    response: Response,
    id: str,
    uid: str = Depends(get_user_id),
):
    """
    __DO NOT__ use this method!
    
    use model specific methods instead, like `[DELETE] /user/avatar/`
    """
    try:
        delete(id, uid)
        response.status_code = status.HTTP_200_OK
        data = {
            'success': True, 
            'message': 'Image has been deleted successfully', 
            'data': None,
        }
    except HTTPException as e:
        data = {'success': False, 'message': e.detail, 'data': None}
        response.status_code = e.status_code
    except Exception as e:
        data = {'success': False, 'message': str(e), 'data': None}
        response.status_code = status.HTTP_406_NOT_ACCEPTABLE
    return data
