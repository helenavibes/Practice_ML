from .models import User, Transaction, PredictionTask, PredictionResult, Base, TransactionType
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
import json
from typing import List, Optional


class DBOperations:
    def __init__(self, db_url: str = "sqlite:///database/app_data.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_user(self, username: str, email: str, password: str) -> int:
        session = self.Session()
        try:
            # Проверка уникальности пользователя
            if session.query(User).filter_by(username=username).first():
                raise ValueError("Username already exists")
            if session.query(User).filter_by(email=email).first():
                raise ValueError("Email already registered")

            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            new_user = User(username=username, email=email, password=hashed_password)
            session.add(new_user)
            session.commit()
            return new_user.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        session = self.Session()
        try:
            return session.query(User).get(user_id)
        finally:
            session.close()

    def get_user_by_username(self, username: str) -> Optional[User]:
        session = self.Session()
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            session.close()

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        session = self.Session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
                return user
            return None
        finally:
            session.close()

    def update_balance(self, user_id: int, amount: float, description: str) -> Transaction:
        session = self.Session()
        try:
            user = session.query(User).get(user_id)
            if not user:
                raise ValueError("User not found")

            # Проверка баланса перед списанием
            if user.balance + amount < 0:
                raise ValueError("Insufficient balance")

            transaction_type = (
                TransactionType.DEPOSIT if amount > 0 else TransactionType.PREDICTION_FEE
            )
            transaction = Transaction(
                user_id=user_id,
                amount=amount,
                description=description,
                transaction_type=transaction_type
            )
            user.balance += amount

            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction
        finally:
            session.close()

    def create_prediction_task(self, user_id: int, model_name: str, input_data: dict) -> PredictionTask:
        session = self.Session()
        try:
            task = PredictionTask(
                user_id=user_id,
                model_name=model_name,
                input_data=json.dumps(input_data)  # сериализация JSON
            )
            session.add(task)
            session.commit()
            session.refresh(task)  # 👈 обязательно до закрытия сессии
            return task
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()

    def create_prediction_result(self, task_id: int, predictions: dict, cost: float) -> PredictionResult:
        session = self.Session()
        try:
            task = session.query(PredictionTask).get(task_id)
            if not task:
                raise ValueError("Prediction task not found")

            # Списание средств
            user = session.query(User).get(task.user_id)
            if not user or user.balance < cost:
                raise ValueError("Insufficient balance")

            user.balance -= cost

            result = PredictionResult(
                task_id=task_id,
                predictions=json.dumps(predictions),
                cost=cost
            )
            session.add(result)

            # Записываем транзакцию
            transaction = Transaction(
                user_id=task.user_id,
                amount=-cost,
                transaction_type=TransactionType.PREDICTION_FEE,
                description=f"Prediction cost for task {task.id}"
            )
            session.add(transaction)

            session.commit()
            session.refresh(result)
            session.expunge(result)
            return result
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def get_transaction_history(self, user_id: int) -> List[Transaction]:
        session = self.Session()
        try:
            return (
                session.query(Transaction)
                .filter_by(user_id=user_id)
                .order_by(Transaction.timestamp.desc())
                .all()
            )
        finally:
            session.close()

    def admin_refill_balance(self, admin_user_id: int, user_id: int, amount: float, reason: str) -> Transaction:
        if amount <= 0:
            raise ValueError("Amount must be positive")

        return self.update_balance(
            user_id=user_id,
            amount=amount,
            description=f"Admin refill: {reason}",
            transaction_type=TransactionType.ADMIN_REFILL
        )

    def get_task_by_id(self, task_id: int) -> Optional[PredictionTask]:
        session = self.Session()
        try:
            return session.query(PredictionTask).get(task_id)
        finally:
            session.close()