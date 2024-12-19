from fastapi import Form, HTTPException, status, APIRouter
from fastapi.security import HTTPBasic
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.models.models import Base

auth = APIRouter()
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:sanji@127.0.0.1/service_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)

# создание сессии для БД
SessionLocal = sessionmaker(autoflush=False, bind=engine)
security = HTTPBasic()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SECRET_KEY = "mugiwaraluffy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


@auth.get("/")
async def root():
    return {"message": "Welcome to the Products API! Use the available endpoints to interact with the database."}
