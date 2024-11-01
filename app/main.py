from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

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

my_app = FastAPI()
feedback_list = []
user_creation: list[UserCreate] = []