from fastapi import FastAPI, Form
from fastapi.params import Depends
from fastapi.responses import FileResponse
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, Person
import random

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:sanji@127.0.0.1/service_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
Base.metadata.create_all(bind=engine)

# создание сессии для БД
SessionLocal = sessionmaker(autoflush=False, bind=engine)

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
