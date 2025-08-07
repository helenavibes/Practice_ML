from pydantic import BaseModel, EmailStr
from typing import List, Dict

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
