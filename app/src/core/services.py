from .models import MLModel, User, PredictionTask, PredictionResult, DataValidationResult
from abc import ABC, abstractmethod

class ServiceInterface(ABC):
    @abstractmethod
    def process_prediction_request(self, user_id: int, model_id: int, data: List[Dict]) -> PredictionResult:
        pass

class RESTInterface(ServiceInterface):
    def process_prediction_request(self, user_id: int, model_id: int, data: List[Dict]) -> PredictionResult:
        # Реализация REST API будет здесь
        pass

class TelegramInterface(ServiceInterface):
    def process_prediction_request(self, user_id: int, model_id: int, data: List[Dict]) -> PredictionResult:
        # Реализация Telegram Bot будет здесь
        pass

class MLService:
    def __init__(self):
        self.__models: Dict[int, MLModel] = {}
        self.__task_queue = []

    def register_model(self, model: MLModel) -> None:
        self.__models[model.model_id] = model

    def create_prediction_task(self, user: User, model_id: int, data: List[Dict]) -> PredictionTask:
        model = self.__models.get(model_id)
        if not model:
            raise ValueError("Model not found")

        if user.balance < model.cost_per_request:
            raise ValueError("Insufficient balance")

        task = PredictionTask(
            task_id=len(self.__task_queue) + 1,
            user_id=user.user_id,
            model_id=model_id,
            raw_data=data
        )
        self.__task_queue.append(task)
        return task

    def process_task(self, task: PredictionTask) -> PredictionResult:
        validation_result = task.validate_data()

        if not validation_result.has_valid_data:
            raise ValueError("No valid data for prediction")

        # Заглушка для реальной ML обработки
        predictions = [f"result_{i}" for i in range(len(validation_result.valid_data))]

        return PredictionResult(
            result_id=len(validation_result.valid_data) + 1,
            user_id=task.user_id,
            model_id=task.model_id,
            input_data=validation_result.valid_data,
            predictions=predictions,
            cost=self.__models[task.model_id].cost_per_request * len(validation_result.valid_data)
        )

class UserRepository:
    def get_user_by_credentials(self, username: str, password_hash: str) -> Optional[User]:
        # Реализация получения пользователя из БД
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        # Реализация получения пользователя по ID
        pass

class TransactionRepository:
    def log_transaction(self, user_id: int, amount: float, transaction_type: TransactionType) -> None:
        # Реализация логирования транзакции
        pass

    def get_user_history(self, user_id: int) -> List[Transaction]:
        # Реализация получения истории транзакций
        pass