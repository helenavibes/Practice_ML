from fastapi import APIRouter, Depends, HTTPException
from app.src.api.dependencies import get_user_repo
from database.repositories import DatabaseUserRepository

router = APIRouter(prefix="/user", tags=["User"])

@router.get("/{user_id}/balance")
async def get_balance(
    user_id: int,
    user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"balance": user.balance}

@router.post("/{user_id}/top-up")
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

    user.update_balance(amount)
    return {"message": "Balance updated", "new_balance": user.balance}

@router.get("/{user_id}/history")
async def get_history(
    user_id: int,
    user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user.history