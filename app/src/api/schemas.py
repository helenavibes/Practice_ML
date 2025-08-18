from pydantic import BaseModel, EmailStr
from typing import List, Dict
from datetime import datetime
from enum import Enum

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PredictionRequest(BaseModel):
    user_id: int
    data: List[Dict]

class ModelResponse(BaseModel):
    id: int
    name: str
    type: str
    cost: float

class TransactionTypeEnum(str, Enum):
    deposit = "deposit"
    prediction_fee = "prediction_fee"
    admin_refill = "admin_refill"


class TransactionOut(BaseModel):
    id: int
    user_id: int
    amount: float
    transaction_type: TransactionTypeEnum
    timestamp: datetime
    description: str | None = None

    class Config:
        from_attributes = True