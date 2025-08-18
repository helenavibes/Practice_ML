from fastapi import APIRouter, HTTPException, Depends, Request
from app.src.core.services import MLService
from app.src.core.models import User, MLModel, MLModelType
from app.src.api.schemas import UserCreate, UserLogin, PredictionRequest, ModelResponse
from database.operations import DBOperations
from app.src.api.schemas import TransactionOut
from app.src.api.dependencies import get_user_repo
from database.repositories import DatabaseUserRepository
import bcrypt
from datetime import datetime
from typing import List

router = APIRouter()

class DatabaseUserRepository:
    def __init__(self, db: DBOperations):
        self.db = db

    def get_user_by_username(self, username: str) -> User | None:
        db_user = self.db.get_user_by_username(username)
        if db_user:
            return User(
                user_id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                password=db_user.password,
                balance=db_user.balance
            )
        return None

    def create_user(self, username: str, email: str, hashed_password: str) -> User:
        db_user = self.db.create_user(username, email, hashed_password)
        return User(
            user_id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            password=db_user.password,
            balance=db_user.balance
        )

    def get_user_by_id(self, user_id: int) -> User | None:
        db_user = self.db.get_user_by_id(user_id)
        if db_user:
            return User(
                user_id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                password=db_user.password,
                balance=db_user.balance
            )
        return None

    def get_transaction_history(self, user_id: int):
        return self.db.get_transaction_history(user_id)


class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(hashed_password: str, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )


async def get_db(request: Request):
    return request.app.state.db

async def get_ml_service(request: Request) -> MLService:
    return request.app.state.ml_service


async def get_user_repo(request: Request) -> DatabaseUserRepository:
    db = await get_db(request)
    return DatabaseUserRepository(db)


@router.get("/")
def root():
    return {"message": "ML Service is running"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/models", response_model=List[ModelResponse])
async def list_models(ml_service: MLService = Depends(get_ml_service)):
    return [
        ModelResponse(
            id=model.model_id,
            name=model.name,
            type=model.model_type.value,
            cost=model.cost_per_request
        )
        for model in ml_service._MLService__models.values()
    ]


@router.get("/user/{user_id}/transactions", response_model=List[TransactionOut])
async def get_transactions(
    user_id: int,
    user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = await user_repo.get_transaction_history(user_id)
    return transactions

@router.get("/balance/{user_id}")
async def get_balance(
        user_id: int,
        user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": user.balance}


@router.post("/balance/{user_id}/top-up")
async def top_up_balance(
        user_id: int,
        amount: float,
        user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # В реальности нужно обновлять через DBOperations
    user.update_balance(amount)
    return {"message": "Balance updated", "new_balance": user.balance}


@router.get("/history/{user_id}")
async def get_history(
        user_id: int,
        user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.history


@router.post("/register")
async def register(
        user: UserCreate,
        user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    if user_repo.get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username exists")

    hashed_pw = PasswordHasher.hash_password(user.password)
    new_user = user_repo.create_user(user.username, user.email, hashed_pw)
    return {"message": "User registered", "user_id": new_user.user_id}


@router.post("/login")
async def login(
        credentials: UserLogin,
        user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = user_repo.get_user_by_username(credentials.username)
    if not user or not PasswordHasher.check_password(user.password, credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.user_id}


@router.post("/predict/{model_id}")
async def predict(
        model_id: int,
        request: PredictionRequest,
        ml_service: MLService = Depends(get_ml_service),
        user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = user_repo.get_user_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        task = ml_service.create_prediction_task(user, model_id, request.data)
        result = ml_service.process_task(task)

        user.history.append({
            "model_id": model_id,
            "input": request.data,
            "result": result.summary,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result.summary
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))