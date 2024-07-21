from hashlib import sha512
from hmac import compare_digest, new
from os import getenv
from random import randint
from secrets import token_hex
from datetime import datetime, timedelta

from bcrypt import checkpw
from fastapi import Header, HTTPException, status
from passlib.context import CryptContext
from beanie import PydanticObjectId

from app.models.user import User



def create_token(identifier: PydanticObjectId) -> str:
    """
    Creates a token including the given identifier.
    The token consists of a random string of 16 bytes (32 hex digits) and a signature.
    The signature is calculated by hashing the concatenation of the random string and the identifier using SHA-512.

    Args:
        identifier (str): The identifier to include in the token.

    Returns:
        str: The generated token.
    """
    identifier = str(identifier)
    randstr = token_hex(16)
    signature = new(
        getenv('SECRET_KEY').encode(), 
        randstr.encode() + identifier.encode(), 
        sha512,
    ).hexdigest()
    return randstr + identifier + signature


def verify_token(token: str) -> str:
    randstr, identifier, signature = token[:32], token[32:56], token[56:]
    identifier = str(identifier)
    calculated_signature = new(
        getenv('SECRET_KEY').encode(), 
        randstr.encode() + identifier.encode(), 
        sha512,
    ).hexdigest()
    if compare_digest(signature, calculated_signature):
        return identifier
    else:
        return ''
 

async def get_user(authorization: str) -> User:
    # Check if authorization string is OK
    if ' ' not in authorization:
        raise Exception('Invalid token!')
    # Obtain user_id from authorization string
    token = authorization.split()[-1]
    uid = verify_token(token)
    if not uid:
        raise Exception('Invalid token!')
    # Get user
    user = await User.get(uid)
    if not user:
        raise Exception('Invalid token!')
    # Check if user is active
    elif user.is_user_active == False:
        raise Exception('User is not active!')
    # Check if token is valid
    for t in user.tokens:
        if checkpw(token.encode('utf-8'), t.encode('utf-8')):
            break
    else:
        raise Exception('Invalid token!')
    return user


async def get_user_id(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header is required',
        )
    try:
        user = await get_user(authorization)
        return user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


async def get_admin_id(authorization: str = Header(None)) -> str:
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header is required',
        )
    try:
        user = await get_user(authorization)
        if not user.is_admin:
            raise Exception('Forbiden!')
        return user.id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
