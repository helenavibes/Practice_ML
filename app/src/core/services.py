from .models import MLModel, User, PredictionTask, PredictionResult, DataValidationResult
from database.operations import DBOperations
import json

class MLService:
    def __init__(self, db: DBOperations):
        self.__models: dict[int, MLModel] = {}
        self.__task_queue = []
        self.db = db

    def register_model(self, model: MLModel) -> None:
        self.__models[model.model_id] = model

    def create_prediction_task(self, user: User, model_id: int, data: list[dict]) -> PredictionTask:
        model = self.__models.get(model_id)
        if not model:
            raise ValueError("Model not found")

        # Получаем актуальный баланс из БД
        db_user = self.db.get_user_by_id(user.user_id)
        if not db_user or db_user.balance < model.cost_per_request * len(data):
            raise ValueError("Insufficient balance")

        # Создаем задачу в БД
        db_task = self.db.create_prediction_task(
            user_id=user.user_id,
            model_name=model.name,
            input_data=data  # Убрали json.dumps()
        )

        return PredictionTask(
            task_id=db_task.id,
            user_id=user.user_id,
            model_id=model_id,
            raw_data=data
        )

    def process_task(self, task: PredictionTask) -> PredictionResult:
        validation_result = task.validate_data()

        if not validation_result.has_valid_data:
            raise ValueError("No valid data for prediction")

        model = self.__models[task.model_id]
        cost = model.cost_per_request * len(validation_result.valid_data)

        # Заглушка для ML обработки
        predictions = [f"result_{i}" for i in range(len(validation_result.valid_data))]

        # Сохраняем результат в БД
        db_result = self.db.create_prediction_result(
            task_id=task.task_id,
            predictions=predictions,  # Исправлено
            cost=cost
        )

        # Обновляем баланс
        self.db.update_balance(
            user_id=task.user_id,
            amount=-cost,
            description=f"Prediction fee for {model.name}"
        )

        return PredictionResult(
            result_id=db_result.id,
            user_id=task.user_id,
            model_id=task.model_id,
            input_data=validation_result.valid_data,
            predictions=predictions,
            cost=cost
        )