from .. import models, schemas
from ..database import SessionLocal
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .password_utils import bcrypt
from dotenv import load_dotenv
import os

load_dotenv()

ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

def create_admin_user():
    try:
        db: Session = SessionLocal()
        new_user = models.Users(
            username="admin",
            email = ADMIN_EMAIL,
            password = bcrypt(ADMIN_PASSWORD),
            role = schemas.Role.admin
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
    
    except IntegrityError:
        db.rollback()
        print("SKIPPING ADMIN USER")

    finally:
        db.close()  