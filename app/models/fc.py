from datetime import date
from typing import Optional
from beanie import Document
from bson import ObjectId
from pydantic import Field, BaseModel

class Flashcard(Document):
    user_id: str  # Keep this as ObjectId for MongoDB references
    question: str
    answer: str
    review_date: date
    level: int = 1

    class Settings:
        collection = "flashcards"
    
    class Config:
        arbitrary_types_allowed = True