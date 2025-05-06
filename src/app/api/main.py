from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.app.api.data_from_db import router
from src.app.api.db_connection import auth

# Создаем приложение FastAPI
app = FastAPI()

# Настраиваем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Разрешаем запросы с фронтенда
    allow_credentials=True,  # Разрешаем cookies/авторизацию
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, и т.д.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(router)
app.include_router(auth)

# if __name__ == "__main__":
#     uvicorn.run(app, host='127.0.0.1', port=8120)