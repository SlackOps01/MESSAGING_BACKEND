from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer
from jose import jwt, JWTError
from dotenv import load_dotenv
import os
from datetime import datetime, timezone, timedelta
from .schemas import TokenData

load_dotenv()

oauth2scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

def create_access_token(data: dict) -> str:
    payload = data.copy()
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload['exp'] = exp
    access_token = jwt.encode(
        payload,
        SECRET_KEY,
        ALGORITHM
    )
    return access_token

def verify_access_token(token: str, credential_exception) -> TokenData:
    try:
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            ALGORITHM
        )
        id = payload.get("id")
        username = payload.get("username")
        role = payload.get("role")
        token_data = TokenData(
            id=id,
            username=username,
            role=role
        )
        return token_data
    
    except JWTError:
        raise credential_exception
    
def get_current_user(token: str = Depends(oauth2scheme)) -> TokenData:
    credential_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized",
            headers={
                "WWW-Authenticate":"Bearer"
            }
        )
    return verify_access_token(token, credential_exception)