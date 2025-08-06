from core.services import MLService
from core.models import MLModel, MLModelType

if __name__ == '__main__':
    print("Инициализация ML сервиса...")

    # Создание экземпляра сервиса
    service = MLService()

    # Регистрация тестовой модели
    service.register_model(
        MLModel(1, "CLI Модель", MLModelType.CLASSIFICATION, 0.3)
    )

    print(f"Зарегистрированные модели: {[m.name for m in service._MLService__models.values()]}")
    print("CLI интерфейс готов. Добавьте ваши команды здесь.")