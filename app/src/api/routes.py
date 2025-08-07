from fastapi import APIRouter, HTTPException
from app.src.core.models import MLModel, MLModelType, User
from app.src.core.services import MLService
from app.src.api.schemas import UserCreate, UserLogin, PredictionRequest, ModelResponse
from typing import List
from datetime import datetime

router = APIRouter()
ml_service = MLService()

# ⚙️ Регистрируем модели
ml_service.register_model(MLModel(1, "Classification", MLModelType.CLASSIFICATION, 0.5))
ml_service.register_model(MLModel(2, "Regression", MLModelType.REGRESSION, 0.7))
ml_service.register_model(MLModel(3, "Clustering", MLModelType.CLUSTERING, 1.0))

# 📦 Заглушка: временное хранилище пользователей
fake_users = {}


@router.get("/")
def root():
    return {"message": "ML Service is running"}


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/models", response_model=List[ModelResponse])
def list_models():
    return [
        ModelResponse(
            id=model.model_id,
            name=model.name,
            type=model.model_type.value,
            cost=model.cost_per_request
        )
        for model in ml_service._MLService__models.values()
    ]

@router.get("/balance/{user_id}")
def get_balance(user_id: int):
    user = next((u for u in fake_users.values() if u.user_id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": user.balance}

@router.post("/balance/{user_id}/top-up")
def top_up_balance(user_id: int, amount: float):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    user = next((u for u in fake_users.values() if u.user_id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.balance += amount
    return {"message": "Balance updated", "new_balance": user.balance}

@router.get("/history/{user_id}")
def get_history(user_id: int):
    user = next((u for u in fake_users.values() if u.user_id == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.history

@router.post("/register")
def register(user: UserCreate):
    if user.username in fake_users:
        raise HTTPException(status_code=400, detail="Username already exists")

    user_id = len(fake_users) + 1
    fake_users[user.username] = User(
        user_id=user_id,
        username=user.username,
        email=user.email,
        password_hash=user.password,  # ❗ лучше хешировать (например, bcrypt)
        balance=100.0
    )
    return {"message": "User registered", "user_id": user_id}


@router.post("/login")
def login(credentials: UserLogin):
    user = fake_users.get(credentials.username)
    if not user or not user.check_password(credentials.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful", "user_id": user.user_id}


@router.post("/predict/{model_id}")
def predict(model_id: int, request: PredictionRequest):
    user = next((u for u in fake_users.values() if u.user_id == request.user_id), None)
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