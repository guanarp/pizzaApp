import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Union, Any

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from jose import jwt
from passlib.context import CryptContext



load_dotenv()


#Constants
ACCESS_TOKEN_EXPIRE_MINUTES = 60*6  # 360 minutes == 6 hours
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 6 #7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']


password_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto" )

def get_hashed_password(password :str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hashed_pass: str) -> bool:
    return password_context.verify(password,hashed_pass)


"""
Create tokens

The functions simply take the payload to include inside the
JWT, which can be anything. Usually you would want to store
information like USER_ID here, but this can be anything from 
strings to objects/dictionaries. The functions return tokens 
as strings.
"""

def create_access_token(
        subject: Union[str, Any], expires_delta: int = None) -> str:
    
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expires_delta, "sub":str(subject)}
    encoded_jwt  = jwt.encode(to_encode, JWT_SECRET_KEY, ALGORITHM)
    return encoded_jwt

def create_refresh_token(
        subject: Union[str, Any], expires_delta: int = None) -> str:
    
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(
            minutes = REFRESH_TOKEN_EXPIRE_MINUTES)

    to_encode = {"exp": expires_delta, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, ALGORITHM)
    return encoded_jwt



