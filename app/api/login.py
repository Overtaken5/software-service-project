import random
import jwt

from fastapi import Form, HTTPException, status, APIRouter
from fastapi.params import Depends
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, OAuth2PasswordRequestForm

from pathlib import Path
from passlib.context import CryptContext
from datetime import timedelta, timezone, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from app.api.models.models import Base, Users

auth = APIRouter()
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

SECRET_KEY = "mugiwaraluffy"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15


@auth.get("/")
async def root():
    file_path = Path("app/frontend/index.html")
    return FileResponse(file_path)


@auth.post("/registration")
async def register(username: str = Form(), user_password: str = Form(), db: Session = Depends(get_db)):
    hashed_password = get_password_hash(user_password)  # Хэшируем пароль
    if username == "kuleshovd":
        role = "admin"
    else:
        role = "guest"
    new_user = Users(username=username, hashed_password=hashed_password,
                     token=str(random.randint(10000, 99999)) + "z", role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User successfully registered", "user_id": new_user.id}


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# функция для сравнения обычного пароля с хэшированным
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


# принимает пароль и возвращает захэшированное значение
def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str, db: Session = Depends(get_db)):
    user = db.query(Users).filter(username == Users.username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def authenticate_user(db, username: str, password: str):
    user = get_user(username, db)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):  # исправлено на user.hashed_password
        return False
    return user


# рут генерации токена по имени пользователя
@auth.post("/login")
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    if not authenticate_user(db, username, password):
        raise HTTPException(status_code=401, detail="Invalid credentials", headers={"WWW-Authenticate": "Basic"})

    access_token = create_access_token(data={"sub": username})
    return {"access_token": access_token, "token_type": "bearer"}


# проверка аутентификации пользователя
@auth.get("/protected_resource")
async def protected_resource(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired", headers={"WWW-Authenticate": "Basic"})
    except jwt.DecodeError:
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Basic"})

    return {"message": "Access granted to protected resource", "user": username}

# роль админа
@auth.get("/admin/")
async def get_admin_info(current_user: str = Depends(protected_resource), db: Session = Depends(get_db)):
    username = current_user["user"]
    user = get_user(username, db)

    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return {"message": f"Welcome admin {user.username}"}


# роль пользователя/гостя
@auth.get("/guest/")
async def get_guest_info(current_user: str = Depends(protected_resource), db: Session = Depends(get_db)):
    username = current_user["user"]
    user = get_user(username, db)

    if user.role != "guest":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return {"message": f"Hello guest {user.username}"}