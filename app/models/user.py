from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from beanie import Document
from pymongo import IndexModel, ASCENDING


class User(Document):
    # TODO: is_mobile/email_validate
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


class Join(BaseModel):
    username: str
    mobile: str
    email: EmailStr
    password: str
    
    class Config:
        json_schema_extra = {'example': {
            'username': 'abc',
            'mobile': '+9876543210',
            'email': 'abc@example.com',
            'password': '123'
        }
    }


class Login(BaseModel):
    usemo: str
    password: str

    class Config:
        json_schema_extra = {'example': {
            'usemo': 'abc',
            'password': '123'
        }
    }


class Username(BaseModel):
    username: Optional[str] = None

    class Config:
        json_schema_extra = {'example': {
            'username': 'abc',
        }
    }
      

class Profile(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None

    class Config:
        json_schema_extra = {'example': {
            'first_name': 'John',
            'last_name': 'Doe',
            'bio': '...',
        }
    }


class Avatar(BaseModel):
    avatar: Optional[str] = None

    class Config:
        json_schema_extra = {'example': {
            'avatar': '< an optimized base64 image ... >',
        }
    }
