from fastapi import FastAPI, Form, Depends, status, HTTPException
from fastapi.params import Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models.models import Base, Person
import random

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:sanji@127.0.0.1/service_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)

# создание сессии для БД
SessionLocal = sessionmaker(autoflush=False, bind=engine)
security = HTTPBasic()

# Функция для получения сессии
def get_db():
    db = SessionLocal()  # создаём экземпляр сессии
    try:
        yield db  # возвращаем сессию для использования
    finally:
        db.close()  # закрываем сессию, чтобы освободить ресурсы

app = FastAPI()
feedback_list = []

@app.get("/")
async def root():
    file_path = Path("app/frontend/index.html")
    return FileResponse(file_path)


@app.post("/registration")
async def register(username: str = Form(), user_password: str = Form(), db: SessionLocal = Depends(get_db)):
    new_user = Person(username=username, password=user_password, token=str(random.randint(1000, 9999)) + "z")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User successfully registered", "user_id": new_user.id}

def get_user_from_db(username: str, db: Session):
    return db.query(Person).filter(Person.username == username).first()


def authenticate_user(credentials: HTTPBasicCredentials = Depends(security), db: Session = Depends(get_db) ):
    user = get_user_from_db(credentials.username, db)
    if user is None or user.password != credentials.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials!")
    return user


@app.get("/protected_resource/")
def get_protected_resource(user: Person = Depends(authenticate_user)):
    return {"message": "You have access to the protected resource!",
            "user_info": {"id": user.id, "username": user.username}}

@app.get("/login")
async def authentication():
    pass

# прогноз продуктов
@app.post("/products_forecast")
async def check_products_amount():
    pass
# выдача количества продукта и прогноза
@app.get("/products_amount")
async def  give_products_amount():
    pass

async def give_forecast():
    pass
