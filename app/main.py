from datetime import datetime, timedelta

from fastapi import FastAPI, Response, status
from fastapi.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from dotenv import load_dotenv
load_dotenv()

from app.database import init_db

from app.api.user import api as user
from app.models import Response_Model


app = FastAPI(
    title='Fast CMS',
    version='0.1.1',
    description='',
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
async def connect():
    await init_db()


app.include_router(user, tags=['Users'], prefix='/user')


@app.get('/time/', response_model=Response_Model, tags=['Time'])
async def server_time(response: Response):
    """
    """
    try:
        now = datetime.now() + timedelta(minutes=int(getenv('DELTA_MINUTES')))
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
