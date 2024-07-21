from datetime import datetime, UTC
from os import getenv

from fastapi import FastAPI, Response, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()

from app.database import init_db

from app.api.user import api as user
from app.admin.user import api as admin_user
from app.models import Response_Model
from app.utils.changelog import get_version, get_change_log


app = FastAPI(
    title='Fast CMS',
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

# static_directory = path.join(path.dirname(__file__), 'static')
# app.mount('/static', StaticFiles(directory=static_directory), name='static')


@app.on_event('startup')
async def connect_to_db():
    await init_db()


app.include_router(user, tags=['Users'], prefix='/user')
app.include_router(admin_user, tags=['Admin - Users'], prefix='/admin/user')


# @app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    messages = []
    for error in errors:
        if error['type'] == 'value_error.jsondecode':
            messages.append({'error': {'message': 'Invalid JSON body'}, 'status': 0})
        else:
            messages.append(error.get('msg', ''))
    response = {
        'success': False,
        'data': None,
        'message': '\n'.join(messages),
    }
    return JSONResponse(content=response, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


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
