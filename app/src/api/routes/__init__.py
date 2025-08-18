from fastapi import APIRouter
from .health import router as health_router
from .auth import router as auth_router
from .ml_models import router as ml_router
from .user import router as user_router
from .transactions import router as transactions_router

router = APIRouter()
router.include_router(health_router)
router.include_router(auth_router)
router.include_router(ml_router)
router.include_router(user_router)
router.include_router(transactions_router)