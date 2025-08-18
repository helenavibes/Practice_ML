from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.src.api.schemas import TransactionOut
from app.src.api.dependencies import get_user_repo
from database.repositories import DatabaseUserRepository

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.get("/{user_id}", response_model=List[TransactionOut])
async def get_transactions(
    user_id: int,
    user_repo: DatabaseUserRepository = Depends(get_user_repo)
):
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transactions = await user_repo.get_transaction_history(user_id)
    return transactions