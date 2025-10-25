from pydantic import BaseModel, EmailStr
from enum import Enum
from datetime import datetime
from typing import Optional

class Role(str, Enum):
    admin="admin"
    user="user"


class TokenData(BaseModel):
    id: str
    username: str
    role: Role

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class MessageCreate(BaseModel):
    sender_id: str
    recipient_id: str
    content: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: Role
    date_created: datetime
    date_updated: datetime | None = None

class MessageResponse(BaseModel):
    id: str
    sender_id: str
    recipient_id: str
    content: str
    timestamp: datetime