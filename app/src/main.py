import os
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.src.api.routes import router  # Раскомментируем импорт роутера
from app.src.core.services import MLService
from database.operations import DBOperations

app = FastAPI()

# Конфигурация базы данных из переменных окружения
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_HOST", "database")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создание движка и сессии
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.on_event("startup")
async def startup_event():
    # Инициализация сервисов
    app.state.db = DBOperations(SQLALCHEMY_DATABASE_URL)
    app.state.ml_service = MLService(app.state.db)
    print("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    # Завершающие операции
    print("Application shutting down")

@app.get("/health")
async def health_check():
    return {"status": "ok", "database": "connected"}

# Подключаем роутер
app.include_router(router, prefix="/api")