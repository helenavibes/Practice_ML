from enum import Enum
from datetime import datetime
from typing import List, Dict, Any
from main import PasswordHasher
import bcrypt

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

class MLModelType(Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"

class TransactionType(Enum):
    DEPOSIT = "deposit"
    PREDICTION_FEE = "prediction_fee"
    ADMIN_REFILL = "admin_refill"

class User:
    def __init__(self, user_id: int, username: str, email: str, password: str, balance: float = 0.0):
        self.__user_id = user_id
        self.__username = username
        self.__email = email
        self.__password = password
        self.__balance = balance
        self.history = []

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def username(self) -> str:
        return self.__username

    @property
    def email(self) -> str:
        return self.__email

    @property
    def balance(self) -> float:
        return self.__balance

    def update_balance(self, amount: float) -> None:
        if self.__balance + amount < 0:
            raise ValueError("Insufficient funds")
        self.__balance += amount

    def check_password(self, password: str) -> bool:
        return PasswordHasher.check_password(self.__password, password)

class Admin(User):
    def __init__(self, user_id: int, username: str, email: str, password_hash: str):
        super().__init__(user_id, username, email, password_hash, balance=0.0)
        self.__is_admin = True

    def replenish_user_balance(self, user: User, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Amount must be positive")
        user.update_balance(amount)

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
    def model_type(self) -> MLModelType:
        return self.__model_type

    @property
    def cost_per_request(self) -> float:
        return self.__cost_per_request

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

class PredictionTask:
    def __init__(self, task_id: int, user_id: int, model_id: int, raw_data: List[Dict]):
        self.task_id = task_id
        self.user_id = user_id
        self.model_id = model_id
        self.raw_data = raw_data
        self.status = "pending"
        self.created_at = datetime.now()
        self.result = None

    def validate_data(self) -> DataValidationResult:
        valid_data = []
        invalid_data = []
        errors = []

        for item in self.raw_data:
            if self._is_valid(item):
                valid_data.append(item)
            else:
                invalid_data.append(item)
                errors.append(f"Invalid item: {item}")

        return DataValidationResult(valid_data, invalid_data, errors)

    def _is_valid(self, data_item: Dict) -> bool:
        return True

class PredictionResult:
    def __init__(self, task: PredictionTask, predictions: List[Any], cost: float):
        self.result_id = id(self)
        self.task_id = task.task_id
        self.user_id = task.user_id
        self.model_id = task.model_id
        self.input_data = task.raw_data
        self.predictions = predictions
        self.cost = cost
        self.timestamp = datetime.now()

    @property
    def summary(self) -> Dict[str, Any]:
        return {
            "result_id": self.result_id,
            "model_id": self.model_id,
            "input_data_count": len(self.input_data),
            "predictions_sample": self.predictions[:3] if self.predictions else [],
            "cost": self.cost,
            "timestamp": self.timestamp
        }