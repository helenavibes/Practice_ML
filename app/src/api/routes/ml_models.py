from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from app.src.core.services import MLService
from app.src.api.dependencies import get_ml_service, get_user_repo
from app.src.api.schemas import ModelResponse, PredictionRequest
from database.repositories import DatabaseUserRepository

router = APIRouter(prefix="/ml", tags=["ML Models"])

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