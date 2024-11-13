from datetime import datetime
from pytz import UTC
from contextlib import asynccontextmanager
from os import getenv

from fastapi import FastAPI, Response, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv


match getenv('env', 'development'):
    case 'development': load_dotenv('env/.env.dev')
    case 'test': load_dotenv('env/.env.test')
    case 'production': load_dotenv('env/.env.prod')
    case _: raise Exception('env has not been saved!')


from app.database import init_db
import app.database as db

from app.models import Response_Model
from app.utils.changelog import get_version, get_change_log

from app.api.user import api as user
from app.api.fc import api as fc
# from app.api.media import api as media

from app.admin.user import api as admin_user
from app.admin.media import api as admin_media


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.fs = await init_db()
    yield


app = FastAPI(
    title='Fast CMS',
    lifespan=lifespan,
    version=get_version(),
    description=get_change_log(),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


app.include_router(user, tags=['Users'], prefix='/user')
app.include_router(fc, tags=['Fc'], prefix='/fc')
# app.include_router(media, tags=['Media'], prefix='/media')

app.include_router(admin_user, tags=['Admin - Users'], prefix='/admin/user')
app.include_router(admin_media, tags=['Admin - Media'], prefix='/admin/media')

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get('/time/', response_model=Response_Model, tags=['Time'])
async def server_time(response: Response):
    """
    """
    try:
        now = datetime.now(UTC)
        response.status_code = status.HTTP_200_OK
        return {
            'success': True,
            'message': 'Hey, we are up!',
            'data': now.isoformat(),
        }
    except Exception as e:
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'success': False,
            'message': str(e),
            'data': None,
        }


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     errors = exc.errors()
#     messages = []
#     for error in errors:
#         if error['type'] == 'value_error.jsondecode':
#             messages.append({'error': {'message': 'Invalid JSON body'}, 'status': 0})
#         else:
#             messages.append(error.get('msg', ''))
#     response = {
#         'success': False,
#         'data': None,
#         'message': '\n'.join(messages),
#     }
#     return JSONResponse(content=response, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


# static_directory = path.join(path.dirname(__file__), 'static')
# app.mount('/static', StaticFiles(directory=static_directory), name='static')
