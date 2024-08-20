from bson import ObjectId
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import StreamingResponse

from app.models.media import Image
from app.models import Response_Model
from app.utils.pagination import paginate
from app.utils.user import get_admin_id
import app.database as db


api = APIRouter()


@api.get('/image/', response_model=Response_Model)
async def get_all_images(
    response: Response,
    uid: str = Depends(get_admin_id),
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
    uid: str = Depends(get_admin_id),
    which: str = Literal['image', 'thumbnail'],
):
    """
    """
    try:
        match which:
            case 'image': field = 'file_id'
            case 'thumbnail': field = 'thumbnail_id'
            case _: raise Exception('Wrong path!')
        #
        image = await Image.get(id)
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
    uid: str = Depends(get_admin_id),
):
    try:
        image = Image.find_one(Image.original_file_id==id)
        #
        image_grid = await db.fs.find_one({"_id": ObjectId(image.file_id)})
        thumbnail_grid = await db.fs.find_one({"_id": ObjectId(image.thumbnail_id)})
        if not all(image_grid, thumbnail_grid):
            raise HTTPException(status_code=404, detail="File not found")
        #
        await db.fs.delete(ObjectId(image.file_id))
        await db.fs.delete(ObjectId(image.thumbnail_id))
        await image.delete()
        #
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
