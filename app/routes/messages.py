from fastapi import APIRouter, Depends, status, HTTPException
from ..oauth2 import get_current_user
from ..database import get_db
from sqlalchemy.orm import Session
from ..schemas import TokenData, MessageResponse
from .. import models
from sqlalchemy import or_


router = APIRouter(
    prefix="/messages",
    tags=['messages']
)


@router.get("/", response_model=list[MessageResponse])
def get_message_history(recipient_id: str, db: Session = Depends(get_db), current_user: TokenData = Depends(get_current_user)):
    messages = db.query(models.Messages).where(
        or_(
            (models.Messages.sender_id == current_user.id) & (models.Messages.recipient_id == recipient_id),
            (models.Messages.recipient_id==current_user.id) & (models.Messages.sender_id==recipient_id) 
        )
    ).all()
    return messages