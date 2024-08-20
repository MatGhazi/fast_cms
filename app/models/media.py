from datetime import datetime

from beanie import Document
from pymongo import ASCENDING


class Image(Document):
    uid: str
    model: str
    field: str
    object_id: str
    file_name: str
    datetime: datetime
    thumbnail_id: str
    full_id: str
    is_public: bool

    class Settings:
        indexes = [
            'uid',
            'model',
            'datetime',
            [
                ('model', ASCENDING),
                ('object_id', ASCENDING),
            ],
            [
                ('uid', ASCENDING),
                ('model', ASCENDING),
            ],
            [
                ('uid', ASCENDING),
                ('model', ASCENDING),
                ('object_id', ASCENDING),
            ],

        ]


class Video(Document):
    uid: str
    model: str
    field: str
    object_id: str
    file_name: str
    datetime: datetime
    _360p: str
    _480p: str
    _720p: str
    _1080p: str
    is_public: bool
    