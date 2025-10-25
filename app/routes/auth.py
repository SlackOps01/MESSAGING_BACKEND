from fastapi import Depends, HTTPException, status, APIRouter
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import models
from ..database import get_db
from sqlalchemy.orm import Session
from ..utils.password_utils import verify_hash
from ..oauth2 import create_access_token


router = APIRouter(
    prefix="/auth",
    tags=['auth']
)

@router.post("/login")
def login(user_cred: OAuth2PasswordRequestForm = Depends(), db: Session=Depends(get_db)):
    user = db.query(models.Users).where(models.Users.username==user_cred.username).first()
    if user is None or not verify_hash(user_cred.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    access_token = create_access_token({
        "id": user.id,
        "username": user.username,
        "role": user.role
    })
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
    
