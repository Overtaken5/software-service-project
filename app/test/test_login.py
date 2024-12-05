import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.api.models.models import Base, Users
from app.api.db_connection import auth, get_db
from app.api.main import app

# Подключение к реальной базе данных PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:sanji@127.0.0.1/service_db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание сессии для реальной базы данных
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Переопределяем зависимость get_db для использования транзакций и отката
@pytest.fixture(scope="function")
def db_session():
    # Открываем соединение и начинаем транзакцию
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session  # Возвращаем сессию для использования в тестах

    # Откат изменений после выполнения теста
    session.close()  # Закрываем сессию
    transaction.rollback()  # Откатываем транзакцию
    connection.close()  # Закрываем соединение

# Переопределение зависимости FastAPI для использования фикстуры db_session
def override_get_db(db_session):
    try:
        db = db_session  # Используем фикстуру db_session для тестов
        yield db
    finally:
        db.close()  # Закрываем сессию после использования

# Включаем маршруты и переопределяем зависимость get_db
app.include_router(auth)
app.dependency_overrides[get_db] = override_get_db

# Фикстура для клиента FastAPI
@pytest.fixture(scope="module")
def client():
    # Создаём тестовый клиент приложения FastAPI
    with TestClient(app) as c:
        yield c

# Пример тестов с откатом изменений после каждого теста

# Тест регистрации пользователя
def test_registration(client, db_session):
    # Отправляем запрос на регистрацию
    response = client.post("/registration", json={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200  # Проверяем, что регистрация успешна
    assert response.json()["message"] == "User successfully registered"  # Проверяем сообщение в ответе

# Тест авторизации пользователя
def test_login(client, db_session):
    # Сначала регистрируем пользователя
    client.post("/registration", json={"username": "test_user", "password": "test_password"})
    # Отправляем запрос на вход
    response = client.post("/login", json={"username": "test_user", "password": "test_password"})
    assert response.status_code == 200  # Проверяем, что вход успешен
    assert "access_token" in response.json()  # Проверяем наличие токена в ответе

# Тест доступа к защищённому ресурсу с использованием токена
def test_protected_resource_with_token(client, db_session):
    # Регистрируем пользователя и получаем токен
    client.post("/registration", json={"username": "test_user", "password": "test_password"})
    login_response = client.post("/login", json={"username": "test_user", "password": "test_password"})
    token = login_response.json().get("access_token")  # Получаем токен из ответа
    assert token is not None  # Проверяем, что токен получен

    # Отправляем запрос к защищённому ресурсу с токеном
    response = client.get("/protected_resource", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200  # Проверяем, что доступ успешен
    assert response.json()["message"] == "Access granted to protected resource"  # Проверяем сообщение в ответе
