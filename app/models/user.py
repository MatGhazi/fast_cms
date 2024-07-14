from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime

from beanie import Document


class User(Document):
    username: str
    mobile: Optional[str] = None
    email: EmailStr
    password: str
    registration_datetime: datetime
    otp: Optional[str] = None
    otp_datetime: Optional[datetime] = None
    tokens: List[str]
    # personal info
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar: Optional[str] = None

    class Settings:
        indexes = [
            'username', 'mobile', 'email'
        ]


class Register(BaseModel):
    username: str
    mobile: Optional[str] = None
    email: EmailStr
    password: str

    @field_validator('password')
    def password_validator(cls, value):
        if len(value) < 6:
            return Exception('Passwords must be atleast 6 charachters.')

    class Config:
        json_schema_extra = {'example': {
            'username': 'abc',
            'mobile': '+9876543210',
            'email': 'abc@example.com',
            'password': '123456',
        }}


class Login(BaseModel):
    usemo: str
    password: str

    class Config:
        json_schema_extra = {'example': {
            'usemo': 'abc',
            'password': '123456',
        }}


class Profile(BaseModel):
    ...
