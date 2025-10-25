from fastapi import APIRouter, Depends, status, HTTPException
from .. import models, schemas
from ..database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..utils.password_utils import bcrypt
from ..oauth2 import get_current_user



router = APIRouter(
    prefix="/users",
    tags=['users'],
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserResponse)
def create_user(blob: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        blob.password = bcrypt(blob.password)
        new_user = models.Users(**blob.model_dump())
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    
@router.get("/", response_model=list[schemas.UserResponse])
def get_users(db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.role != schemas.Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Method not allowed!"
        )
    users = db.query(models.Users).all()
    return users

@router.get("/{username}", response_model=schemas.UserResponse)
def get_user_by_user_name(username: str, db: Session = Depends(get_db)):
    user = db.query(models.Users).where(models.Users.username == username).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
    return user


@router.put("/{username}", status_code=status.HTTP_202_ACCEPTED,  response_model=schemas.UserResponse)
def update_user(blob: schemas.UserUpdate, username: str, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    user_query = db.query(models.Users).where(models.Users.username==username)
    user = user_query.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if current_user.id != user.id and current_user.role != schemas.Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Method not allowed!"
        )
    data = blob.model_dump(exclude_unset=True)
    if blob.password:
        data['password'] = bcrypt(blob.password)
    user_query.update(data, synchronize_session=False)
    

    db.commit()
    new_username = data.get("username", username)
    new_user = db.query(models.Users).where(models.Users.username==new_username).first()
    return new_user


@router.delete("/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str, db: Session = Depends(get_db), current_user: schemas.TokenData = Depends(get_current_user)):
    if current_user.username != username and current_user.role != schemas.Role.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN
        )
    
    user = db.query(models.Users).where(models.Users.username==username).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found!"
        )
    
    db.delete(user)
    db.commit()
    return 


    