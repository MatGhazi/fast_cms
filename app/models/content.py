from pydantic import BaseModel, field_validator
from typing import Optional, Literal, List, Dict
from datetime import datetime
from os import getenv
from re import compile

from beanie import Document
from pymongo import IndexModel, ASCENDING
from pymongo import MongoClient


class Content(Document):
    uid: str
    datetime: datetime
    model: str
    object_id: str
    title: Optional[str] = None
    cover: Optional[str] = None  # cover image
    photos: Optional[List[str]] = None
    video: Optional[str] = None
    text: Optional[str] = None
    tags: Optional[List[str]] = None
    _search_str: Optional[str] = None

    class Settings:
        indexes = [
            'uid',
            'datetime',
            'model',
            'object_id',
        ]
    

class Comment(Document):
    uid: str
    datetime: datetime
    content_id: Optional[str] = None
    comment_id: Optional[str] = None  # in reply to
    text: str

    class Settings:
        indexes = [
            'datetime',
            'content_id',
            'comment_id',
        ]


class Reaction(Document):
    uid: str
    datetime: datetime
    content_id: Optional[str] = None
    comment_id: Optional[str] = None
    text: str  # :smile:

    class Settings:
        indexes = [
            'datetime',
            'content_id',
            'comment_id',
        ]


class Tag(Document):
    kind: str  # text / user / time / geo
    text: Optional[str] = None
    user: Optional[str] = None
    datetime: Optional[datetime] = None
    geo: Optional[List] = None
    contents: Dict = {}  # keys: object-id, values: model (Content or Comment) ??????????????

    class Settings:
        indexes = []
