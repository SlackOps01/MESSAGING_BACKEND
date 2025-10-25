from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import get_db, engine
from . import models
from .utils.admin_setup import create_admin_user
from .routes import auth, users, messages
from .routes.websockets import chat

models.Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        print("APP STARTING")
        create_admin_user()
        yield
    finally:
        print("app shutting down")


app = FastAPI(
    title="Chat App",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(messages.router)
app.include_router(chat.router)

@app.get("/")
def home():
    return {
        "message": "Hi bitches!"
    }