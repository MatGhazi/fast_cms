from hashlib import sha512
from hmac import compare_digest, new
from random import choices
from string import digits
from secrets import token_hex
from datetime import datetime, timedelta, UTC

from bcrypt import hashpw, gensalt, checkpw
from fastapi import BackgroundTasks, Header, HTTPException, status
from beanie import PydanticObjectId

from app.models.user import User
from app.utils.email import send_email
import app.settings as settings


otp_store = {}


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
        settings.SECRET_KEY.encode(), 
        randstr.encode() + identifier.encode(), 
        sha512,
    ).hexdigest()
    return randstr + identifier + signature


def verify_token(token: str) -> str:
    randstr, identifier, signature = token[:32], token[32:56], token[56:]
    calculated_signature = new(
        settings.SECRET_KEY.encode(), 
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
        return str(user.id)
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


async def send_otp(user, background_tasks: BackgroundTasks):
    now = datetime.now(UTC).replace(tzinfo=None)
    if user.otp_datetime:
        otp_datetime = user.otp_datetime + timedelta(minutes=settings.OTP.wait)
        if otp_datetime > now:
            raise Exception(f'You can request OTP only once in {settings.OTP.wait} minutes!')
    #
    otp = ''.join(choices(digits, k=settings.OTP.length))
    user.otp = hashpw(otp.encode('utf-8'), gensalt(rounds=settings.HASHING_COST)).decode('utf-8')
    user.otp_datetime = now
    await user.save()
    otp_store[user.email] = otp
    #
    # TODO: Sending OTP
    #
    print(f' ~~~ OTP: {otp} ~~~')
    print()
    # await send_email(
    #     background_tasks,
    #     recipient=user.email,
    #     subject='Your OTP Code',
    #     template_name='otp.html',
    #     body={'recipient_name': user.first_name, 'otp':otp}
    # )


def check_otp(user, otp):
    if not user.otp:
        raise Exception('Invalid OTP')
    #
    now = datetime.now(UTC).replace(tzinfo=None)
    otp_is_expired = now > user.otp_datetime + timedelta(minutes=settings.OTP.expiry)
    if otp_is_expired:
        raise Exception('Expired OTP')
    #
    if not checkpw(otp.encode('utf-8'), user.otp.encode('utf-8')):
        raise Exception('Invalid OTP')

