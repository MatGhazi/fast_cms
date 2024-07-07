from os import getenv

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from app.models.user import User


MODELS = [User]

# Initialize the database
async def init_db():
    client = AsyncIOMotorClient(getenv('MONGO_URI'))
    db = client.get_database()
    await init_beanie(database=db, document_models=MODELS)
