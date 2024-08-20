from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
from os import getenv
from re import compile

from beanie import Document
from pymongo import IndexModel, ASCENDING
from pymongo import MongoClient


class Page(Document):
    uid: str
    datetime: datetime
   
    ...


