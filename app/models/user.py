from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from os import getenv
from re import compile

from beanie import Document
from pymongo import IndexModel, ASCENDING
from pymongo import MongoClient

from app.texts.errors import *
from app.texts import get_deletion_reasons
import app.settings as settings


SYNC_DB = MongoClient(getenv('MONGO_URI')).get_database()
USERNAME_REGEX = r'^(?!.*__)(?!_)(?![0-9])[a-zA-Z0-9_]{4,16}(?<!_)$'
PASSWORD_REGEX = r'''^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&_\-+=#^(){}[\]<>.,;:'"`~])[A-Za-z\d@$!%*?&_\-+=#^(){}[\]<>.,;:'"`~]{6,20}$'''
MOBILE_REGEX = r'^\+?[1-9]\d{10,14}$'
EMAIL_REGEX = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
OTP_REGEX = r'^\d{' + str(settings.OTP.length) + r'}$'


# ~~~~~~~~~~ DATABASE MODELS ~~~~~~~~~~ #

class User(Document):
    # Systematic Details
    username: str
    mobile: str
    email: str
    password: str
    registration_datetime: datetime
    otp: Optional[str] = None
    otp_datetime: Optional[datetime] = None
    tokens: Optional[List[str]] = []
    is_user_active: bool
    is_admin: bool
    is_mobile_verified: Optional[bool] = False
    is_email_verified: Optional[bool] = False
    # Personal Info
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None

    class Settings:
        indexes = [
            IndexModel([('username', ASCENDING)], unique=True),
            IndexModel([('mobile', ASCENDING)], unique=True),
            IndexModel([('email', ASCENDING)], unique=True),
        ]

    def get_profile(self):
        return {
            'username': self.username,
            'mobile': self.mobile,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'bio': self.bio,
            'avatar': self.avatar,
        }

    def get_details(self):
        return {
            'id': str(self.id),
            'is_user_active': self.is_user_active,
            'is_admin': self.is_user_active,
        }


class Deletion_Request(Document):
    uid: str
    datetime: datetime
    is_deleted: bool
    reason: str

    class Settings:
        indexes = [
            'uid',
            'datetime',
            'is_deleted',
            [
                ('datetime', ASCENDING),
                ('is_deleted', ASCENDING),
            ],
        ]


# ~~~~~~~~~~ REQUEST MODELS ~~~~~~~~~~ #

class Join(BaseModel):
    username: str
    mobile: str
    email: str
    password: str

    @field_validator('username')
    def validate_username(cls, value):
        if not compile(USERNAME_REGEX).match(value):
            raise ValueError(USERNAME_ERROR)
        if SYNC_DB['User'].find_one({'username': value}):
            raise ValueError(f'Sorry! "{value}" has been taken.')
        return value
    
    @field_validator('password')
    def validate_password(cls, value):
        if not compile(PASSWORD_REGEX).match(value):
            raise ValueError(PASSWORD_ERROR)
        return value
    
    @field_validator('mobile')
    def validate_mobile(cls, value):
        if not compile(MOBILE_REGEX).match(value):
            raise ValueError(MOBILE_ERROR)
        if SYNC_DB['User'].find_one({'mobile': value}):
            raise ValueError(MOBILE_REGISTERED)
        return value
    
    @field_validator('email')
    def validate_email(cls, value):
        if not compile(EMAIL_REGEX).match(value):
            raise ValueError(EMAIL_ERROR)
        if SYNC_DB['User'].find_one({'email': value}):
            raise ValueError(EMAIL_REGISTERED)
        return value

    model_config = ConfigDict(
        json_schema_extra = {'example': {
            'username': 'john_doe',
            'mobile': '+9876543210',
            'email': 'john.doe@example.com',
            'password': 'ABab12*$'
            }
        } 
    )


class Login(BaseModel):
    usemo: str
    password: str

    model_config = ConfigDict(
        json_schema_extra = {'example': {
            'usemo': 'abc',
            'password': '123'
            }
        } 
    )


class Username(BaseModel):
    username: str

    @field_validator('username')
    def validate_username(cls, value):
        if not compile(USERNAME_REGEX).match(value):
            raise ValueError(USERNAME_ERROR)
        if SYNC_DB['User'].find_one({'username': value}):
            raise ValueError(f'Sorry! "{value}" has been taken.')
        return value
    
    model_config = ConfigDict(
        json_schema_extra = {'example': {
            'username': 'john_doe',
            }
        } 
    )
      

class Profile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None

    model_config = ConfigDict(
        json_schema_extra = {'example': {
            'first_name': 'John',
            'last_name': 'Doe',
            'bio': '...',
            }
        } 
    )


class Usemo(BaseModel):
    usemo: str

    model_config = ConfigDict(
        json_schema_extra = {'example': {
            'usemo': '...',
            }
        } 
    )


class Password(BaseModel):
    usemo: str
    otp: str
    password: str

    @field_validator('otp')
    def validate_otp(cls, value):
        if not compile(OTP_REGEX).match(value):
            raise ValueError(OTP_ERROR)
        return value
    
    @field_validator('password')
    def validate_password(cls, value):
        if not compile(PASSWORD_REGEX).match(value):
            raise ValueError(PASSWORD_ERROR)
        return value

    model_config = ConfigDict(
        json_schema_extra = {'example': {
            'usemo': 'john_doe',
            'otp': '112233',
            'password': 'ABab12*$'
            }
        } 
    )


class Delete_Me(BaseModel):
    reason: str

    @field_validator('reason')
    def validate_reason(cls, value):
        if not value:
            raise ValueError(REASON_IS_REQUIRED)
        predefined_reasons = get_deletion_reasons()
        custom_reason = value.startswith('+')
        if value not in predefined_reasons and not custom_reason:
            raise ValueError(INVALID_REASON)
        return value

    model_config = ConfigDict(
        json_schema_extra = {'example': {
            'reason': '...',
            }
        } 
    )

