from os import getenv

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorGridFSBucket

from app.models.user import User, Deletion_Request
from app.models.media import Image, Video
from app.models.content import Content, Comment, Reaction, Tag
from app.models.page import Page
from app.models.fc import Flashcard  

fs = None
MODELS = []
MODELS += [User, Deletion_Request]
MODELS += [Image, Video]
MODELS += [Content, Comment, Reaction, Tag]
MODELS += [Page, Flashcard]


# Initialize the database
async def init_db():
    client = AsyncIOMotorClient(getenv('MONGO_URI'))
    db = client.get_database()
    await init_beanie(database=db, document_models=MODELS)
    fs = AsyncIOMotorGridFSBucket(db)
    return fs
