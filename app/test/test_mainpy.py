import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import sys

# Добавляем путь к родительской директории, чтобы импортировать main
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.models.models import Base, Users, Product
import app.main
from app.main import app, get_db

# SQLALCHEMY_DATABASE_URL для тестирования
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:sanji@127.0.0.1/service_db"

# Настройка тестовой базы данных
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Создаем таблицы в тестовой БД
Base.metadata.create_all(bind=engine)

# Переопределяем зависимость для получения сессии БД на время теста
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Инициализация TestClient для FastAPI
client = TestClient(app)

# Фикстура для создания тестовых пользователей в БД
@pytest.fixture
def create_test_user():
    db = TestingSessionLocal()
    test_user = Users(username="testuser", hashed_password=app.main.get_password_hash("testpassword"), token="12345z", role="guest")
    db.add(test_user)
    db.commit()
    db.refresh(test_user)
    yield test_user
    db.query(Users).filter_by(username="testuser").delete()
    db.commit()
    db.close()

@pytest.fixture
def create_admin_user():
    db = TestingSessionLocal()
    admin_user = Users(username="adminuser", hashed_password=app.main.get_password_hash("adminpassword"), token="67890z", role="admin")
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    yield admin_user
    db.query(Users).filter_by(username="adminuser").delete()
    db.commit()
    db.close()

@pytest.fixture
def create_test_product():
    db = TestingSessionLocal()
    test_product = Product(name="test_product", quantity=10)
    db.add(test_product)
    db.commit()
    db.refresh(test_product)
    yield test_product
    db.query(Product).filter_by(name="test_product").delete()
    db.commit()
    db.close()

# Тест главной страницы
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

# Тест регистрации нового пользователя
def test_register_user():
    response = client.post("/registration", data={"username": "newuser", "user_password": "newpassword"})
    assert response.status_code == 200
    assert response.json()["message"] == "User successfully registered"

# Тест на неудачный вход с неверными данными
def test_login_invalid_user(create_test_user):
    response = client.post("/login", data={"username": "wronguser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials"}

# Тест успешного входа
def test_login_valid_user(create_test_user):
    response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

# Тест доступа к защищенному ресурсу с валидным токеном
def test_protected_resource(create_test_user):
    # Получаем токен
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    # Доступ к защищенному ресурсу
    response = client.get("/protected_resource", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": "Access granted to protected resource", "user": "testuser"}

# Тест доступа к защищенному ресурсу без токена
def test_protected_resource_no_token():
    response = client.get("/protected_resource")
    assert response.status_code == 401
    assert response.json() == {"detail": "Not authenticated"}

# Тест доступа к защищенному ресурсу с недействительным токеном
def test_protected_resource_invalid_token():
    response = client.get("/protected_resource", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid token"}

# Тест для роли администратора
def test_admin_access(create_admin_user):
    login_response = client.post("/login", data={"username": "adminuser", "password": "adminpassword"})
    token = login_response.json()["access_token"]

    response = client.get("/admin/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": f"Welcome admin adminuser"}

# Тест для гостевой роли
def test_guest_access(create_test_user):
    login_response = client.post("/login", data={"username": "testuser", "password": "testpassword"})
    token = login_response.json()["access_token"]

    response = client.get("/guest/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"message": f"Hello guest testuser"}

# Тест получения количества продуктов
def test_product_amount_page():
    response = client.get("/products_amount")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]

# Тест получения количества конкретного продукта
def test_product_amount(create_test_product):
    response = client.post("/products_amount", data={"product_name": "test_product"})
    assert response.status_code == 200
    assert "test_product" in response.text
    assert "10" in response.text

# Тест на несуществующий продукт
def test_product_not_found():
    response = client.post("/products_amount", data={"product_name": "non_existent_product"})
    assert response.status_code == 200
    assert "The product was not found" in response.text
