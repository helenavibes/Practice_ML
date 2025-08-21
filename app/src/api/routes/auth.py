from fastapi import APIRouter, Depends, HTTPException
from app.src.api.schemas import UserCreate, UserLogin
from app.src.api.dependencies import get_user_repo
from database.repositories import DatabaseUserRepository
import bcrypt

router = APIRouter(prefix="/auth", tags=["Auth"])

class PasswordHasher:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def check_password(hashed_password: str, password: str) -> bool:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

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