from database.operations import DBOperations
from app.src.core.models import User


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