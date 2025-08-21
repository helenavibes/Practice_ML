import sys
import os
import bcrypt
import json
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Добавляем родительскую директорию в путь поиска модулей
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.models import Base, User, Transaction, PredictionTask, PredictionResult, TransactionType
from database.operations import DBOperations


def init_database():
    # Создаем временную базу данных в памяти
    temp_db_url = "sqlite:///:memory:"
    print("Creating temporary in-memory database...")

    # Инициализируем DBOperations с временной базой
    temp_db = DBOperations(db_url=temp_db_url)

    # Создаем все таблицы во временной базе
    Base.metadata.create_all(temp_db.engine)
    print("Database schema created")

    # Создаем сессию для работы с базой
    session = Session(bind=temp_db.engine)

    try:
        print("Creating demo users...")

        # Создаем администратора
        admin = User(
            username="admin_demo",
            email="admin@example.com",
            password=bcrypt.hashpw("admin_password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        session.add(admin)

        # Создаем обычного пользователя
        user = User(
            username="user_demo",
            email="user@example.com",
            password=bcrypt.hashpw("user_password".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        )
        session.add(user)

        session.commit()
        session.refresh(admin)
        session.refresh(user)
        print("Users created")

        print("Creating demo transactions...")

        # Функция для добавления транзакции
        def add_transaction(user_obj, amount, description, transaction_type=None):
            if transaction_type is None:
                transaction_type = TransactionType.DEPOSIT if amount > 0 else TransactionType.PREDICTION_FEE

            user_obj.balance += amount
            transaction = Transaction(
                user_id=user_obj.id,
                amount=amount,
                transaction_type=transaction_type,
                description=description
            )
            session.add(transaction)
            return transaction

        # Административное пополнение
        add_transaction(admin, 1000.0, "Initial admin bonus", TransactionType.ADMIN_REFILL)

        # Пользовательские транзакции
        add_transaction(user, 500.0, "Welcome bonus")
        add_transaction(user, -150.0, "Purchase: Groceries")
        add_transaction(user, 300.0, "Deposit from bank")

        print("Creating demo prediction task...")

        # Создаем демо-задачу предсказания
        task = PredictionTask(
            user_id=user.id,
            model_name="classification",
            input_data=json.dumps({"feature1": 5.1, "feature2": 3.5})
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Создаем демо-результат
        result = PredictionResult(
            task_id=task.id,
            predictions=json.dumps({"class": "setosa", "probability": 0.95}),
            cost=10.0
        )
        session.add(result)

        # Списание средств за предсказание
        add_transaction(user, -10.0, "Prediction fee for classification model")

        session.commit()
        print("Demo data created in temporary database")

        # Создаем новое подключение к файловой базе
        db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'app_data.db'))
        print(f"Exporting to: {db_path}")
        file_engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(file_engine)

        # Создаем сессию для файловой базы
        file_session = Session(bind=file_engine)

        # Список всех моделей для копирования
        models = [User, Transaction, PredictionTask, PredictionResult]

        # Копируем данные для каждой модели
        for model in models:
            objects = session.query(model).all()
            for obj in objects:
                # Создаем новый объект без привязки к старой сессии
                new_obj = model()
                for key, value in obj.__dict__.items():
                    if key != '_sa_instance_state':
                        setattr(new_obj, key, value)
                file_session.add(new_obj)

        file_session.commit()
        file_session.close()

        print("Database exported successfully!")
        print(f"Admin: {admin.username}, Balance: {admin.balance}")
        print(f"User: {user.username}, Balance: {user.balance}")

    finally:
        session.close()


if __name__ == "__main__":
    init_database()