from hashlib import sha512
from hmac import compare_digest, new
from os import getenv
from random import randint
from secrets import token_hex
from datetime import datetime, timedelta

from passlib.context import CryptContext

from fastapi import Header, HTTPException, status

from app.models.user import User


def create_token(identifier: str) -> str:
    """
    Creates a token including the given identifier.
    The token consists of a random string of 16 bytes (32 hex digits) and a signature.
    The signature is calculated by hashing the concatenation of the random string and the identifier using SHA-512.

    Args:
        identifier (Any): The identifier to include in the token.

    Returns:
        str: The generated token.
    """
    randstr = token_hex(16)  # generate 8 bytes (32 hex digits)
    signature = new(
        getenv('SECRET_KEY').encode(),
        randstr.encode() + identifier.encode(),
        sha512,
    ).hexdigest()
    return randstr + identifier + signature


def verify_token(token: str) -> str:
    randstr, identifier, signature = token[:32], token[32:56], token[56:]
    calculated_signature = new(
        getenv('SECRET_KEY').encode(),
        randstr.encode() + identifier.encode(),
        sha512,
    ).hexdigest()
    if compare_digest(signature, calculated_signature):
        return identifier
    return ''


async def check_user(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header is required',
        )
    #
    try:
        #
        if ' ' not in authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        token = authorization.split()[-1]
        uid = verify_token(token)
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        #
        user = await User.get(uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        #
        if token not in user.tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        #
        return dict(
            uid=uid,
            # token=token,
        )

    #
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )


async def check_admin(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authorization header is required',
        )
    try:
        #
        if ' ' not in authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        token = authorization.split()[-1]
        uid = verify_token(token)
        if not uid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        #
        user = await User.get(uid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        #
        if token not in user.tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Invalid token!',
            )
        #
        if not user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Forbiden!',
            )
        return dict(
            uid=uid,
            token=token,
        )
    
    #
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )




async def check_admin(authorization: str = Header(None)):
    return True