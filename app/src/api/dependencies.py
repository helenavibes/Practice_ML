from database.operations import DBOperations
from database.repositories import DatabaseUserRepository
from app.src.core.services import MLService
from sqlalchemy import create_engine
import os


def get_db_operations():
    DB_USER = os.getenv("POSTGRES_USER")
    DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    DB_HOST = os.getenv("POSTGRES_HOST", "database")
    DB_PORT = os.getenv("POSTGRES_PORT", "5432")
    DB_NAME = os.getenv("POSTGRES_DB")

    db_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return DBOperations(db_url)


def get_user_repo():
    return DatabaseUserRepository(get_db_operations())


def get_ml_service():
    db_ops = get_db_operations()
    return MLService(db_ops)