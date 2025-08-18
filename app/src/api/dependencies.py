from fastapi import Request
from database.repositories import DatabaseUserRepository
from app.src.core.services import MLService


async def get_db(request: Request):
    return request.app.state.db


async def get_user_repo(request: Request) -> DatabaseUserRepository:
    db = await get_db(request)
    return DatabaseUserRepository(db)


async def get_ml_service(request: Request) -> MLService:
    return request.app.state.ml_service