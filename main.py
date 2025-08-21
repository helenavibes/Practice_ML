from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import List, Dict, Any, Optional
import bcrypt
from app import create_app
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = create_app()

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

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

class User:
    def __init__(self, user_id: int, username: str, email: str, password_hash: str):
        self.__user_id = user_id
        self.__username = username
        self.__email = email
        self.__password_hash = password_hash

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def username(self) -> str:
        return self.__username

    @property
    def email(self) -> str:
        return self.__email

    def check_password(self, password: str) -> bool:
        return PasswordHasher.check_password(self.__password_hash, password)


class Balance:
    def __init__(self, user_id: int, current_balance: float = 0.0):
        self.__user_id = user_id
        self.__balance = current_balance

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def current_balance(self) -> float:
        return self.__balance

    def update_balance(self, amount: float) -> None:
        if self.__balance + amount < 0:
            raise ValueError("Insufficient funds")
        self.__balance += amount


class Admin(User):
    def __init__(self, user_id: int, username: str, email: str, password_hash: str):
        super().__init__(user_id, username, email, password_hash)
        self.__is_admin = True

    def replenish_user_balance(self, balance: Balance, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        balance.update_balance(amount)


class MLModelType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"


class MLModel:
    def __init__(self, model_id: int, name: str, model_type: MLModelType, cost_per_request: float):
        self.__model_id = model_id
        self.__name = name
        self.__model_type = model_type
        self.__cost_per_request = cost_per_request

    @property
    def model_id(self) -> int:
        return self.__model_id

    @property
    def name(self) -> str:
        return self.__name

    @property
    def cost_per_request(self) -> float:
        return self.__cost_per_request


class TransactionType(Enum):
    DEPOSIT = "deposit"
    PREDICTION_FEE = "prediction_fee"
    ADMIN_REFILL = "admin_refill"


class Transaction:
    def __init__(self, transaction_id: int, user_id: int, amount: float,
                 transaction_type: TransactionType, timestamp: datetime = datetime.now()):
        self.__transaction_id = transaction_id
        self.__user_id = user_id
        self.__amount = amount
        self.__type = transaction_type
        self.__timestamp = timestamp

    @property
    def transaction_id(self) -> int:
        return self.__transaction_id

    @property
    def details(self) -> Dict[str, Any]:
        return {
            "user_id": self.__user_id,
            "amount": self.__amount,
            "type": self.__type.value,
            "timestamp": self.__timestamp
        }


class DataValidationResult:
    def __init__(self, valid_data: List[Dict], invalid_data: List[Dict], errors: List[str]):
        self.__valid_data = valid_data
        self.__invalid_data = invalid_data
        self.__errors = errors

    @property
    def valid_data(self) -> List[Dict]:
        return self.__valid_data

    @property
    def invalid_data(self) -> List[Dict]:
        return self.__invalid_data

    @property
    def has_valid_data(self) -> bool:
        return len(self.__valid_data) > 0


class PredictionResult:
    def __init__(self, result_id: int, user_id: int, model_id: int,
                 input_data: List[Dict], predictions: List[Any], cost: float):
        self.__result_id = result_id
        self.__user_id = user_id
        self.__model_id = model_id
        self.__input_data = input_data
        self.__predictions = predictions
        self.__cost = cost
        self.__timestamp = datetime.now()

    @property
    def summary(self) -> Dict[str, Any]:
        return {
            "result_id": self.__result_id,
            "model_id": self.__model_id,
            "input_data_count": len(self.__input_data),
            "predictions_sample": self.__predictions[:3],
            "cost": self.__cost,
            "timestamp": self.__timestamp
        }

class PredictionTask:
    def __init__(self, task_id: int, user_id: int, model_id: int, raw_data: List[Dict]):
        self.__task_id = task_id
        self.__user_id = user_id
        self.__model_id = model_id
        self.__raw_data = raw_data
        self.__status = "pending"
        self.__created_at = datetime.now()

    def validate_data(self) -> DataValidationResult:
        valid_data = []
        invalid_data = []
        errors = []

        for item in self.__raw_data:
            if self._is_valid(item):
                valid_data.append(item)
            else:
                invalid_data.append(item)
                errors.append(f"Invalid item: {item}")

        return DataValidationResult(valid_data, invalid_data, errors)

    def _is_valid(self, data_item: Dict) -> bool:
        return True


class ServiceInterface(ABC):
    @abstractmethod
    def process_prediction_request(self, user_id: int, model_id: int, data: List[Dict]) -> PredictionResult:
        pass


class RESTInterface(ServiceInterface):
    def process_prediction_request(self, user_id: int, model_id: int, data: List[Dict]) -> PredictionResult:
        pass


class TelegramInterface(ServiceInterface):
    def process_prediction_request(self, user_id: int, model_id: int, data: List[Dict]) -> PredictionResult:
        pass


class MLService:
    def __init__(self):
        self.__models: Dict[int, MLModel] = {}
        self.__task_queue = []

    def register_model(self, model: MLModel) -> None:
        self.__models[model.model_id] = model

    def create_prediction_task(self, user_balance: Balance, model_id: int, data: List[Dict]) -> PredictionTask:
        model = self.__models.get(model_id)
        if not model:
            raise ValueError("Model not found")

        total_cost = model.cost_per_request * len(data)
        if user_balance.current_balance < total_cost:
            raise ValueError("Insufficient balance")

        task = PredictionTask(
            task_id=len(self.__task_queue) + 1,
            user_id=user_balance.user_id,
            model_id=model_id,
            raw_data=data
        )
        self.__task_queue.append(task)
        return task

    def process_task(self, task: PredictionTask, user_balance: Balance) -> PredictionResult:
        validation_result = task.validate_data()

        if not validation_result.has_valid_data:
            raise ValueError("No valid data for prediction")

        model = self.__models[task.model_id]
        predictions = [f"result_{i}" for i in range(len(validation_result.valid_data))]

        actual_cost = model.cost_per_request * len(validation_result.valid_data)
        user_balance.update_balance(-actual_cost)

        return PredictionResult(
            result_id=len(validation_result.valid_data) + 1,
            user_id=task.user_id,
            model_id=task.model_id,
            input_data=validation_result.valid_data,
            predictions=predictions,
            cost=actual_cost
        )


class UserRepository:
    def get_user_by_credentials(self, username: str, password: str) -> Optional[User]:
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass


class BalanceRepository:
    def get_user_balance(self, user_id: int) -> Optional[Balance]:
        pass

    def update_user_balance(self, balance: Balance) -> None:
        pass


class TransactionRepository:
    def log_transaction(self, user_id: int, amount: float, transaction_type: TransactionType) -> None:
        pass

    def get_user_history(self, user_id: int) -> List[Transaction]:
        pass


# Create Blueprint instance
class Blueprint:
    pass
