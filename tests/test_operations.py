import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
import json
from database.operations import DBOperations
from database.models import Base, User, Transaction, PredictionTask, PredictionResult, TransactionType
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestDBOperations(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)

        # Исправленная инициализация DBOperations
        self.db = DBOperations(db_url='sqlite:///:memory:')

        # Создаем пользователя и сохраняем его ID
        self.test_user_id = self.db.create_user(
            username="test_user",
            email="test@example.com",
            password="test_password"
        )
        self.test_user = self.db.get_user_by_id(self.test_user_id)

    def test_create_user(self):
        user = self.db.get_user_by_username("test_user")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test@example.com")

        # Проверка пароля через метод модели
        self.assertTrue(user.check_password("test_password"))

        # Проверка хеширования
        self.assertFalse(user.check_password("wrong_password"))

    def update_balance(self, user_id: int, amount: float, description: str) -> Transaction:
        session = self.Session()
        try:
            user = session.query(User).get(user_id)
            if not user:
                raise ValueError("User not found")

            if amount < 0 and user.balance + amount < 0:
                raise ValueError("Insufficient balance")

            transaction_type = (
                TransactionType.DEPOSIT if amount > 0 else TransactionType.PREDICTION_FEE
            )

            user.balance += amount
            transaction = Transaction(
                user_id=user.id,
                amount=amount,
                transaction_type=transaction_type,
                description=description
            )
            session.add(transaction)
            session.commit()
            session.refresh(transaction)
            return transaction
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_insufficient_balance(self):
        user = self.db.get_user_by_id(self.test_user_id)
        # Сброс баланса в 0 для надёжности
        self.db.update_balance(user.id, -user.balance, "Reset balance to zero")

        # Пытаемся списать больше, чем есть
        with self.assertRaises(ValueError):
            self.db.update_balance(user.id, -50.0, "Attempt to overdraft")

    def test_transaction_history(self):
        self.db.update_balance(self.test_user_id, 200.0, "First transaction")
        self.db.update_balance(self.test_user_id, -50.0, "Second transaction")

        history = self.db.get_transaction_history(self.test_user_id)
        self.assertEqual(len(history), 2)

        # Проверяем порядок транзакций (последняя должна быть первой)
        self.assertEqual(history[0].description, "Second transaction")
        self.assertEqual(history[1].description, "First transaction")

    def test_authentication(self):
        # Успешная аутентификация
        user = self.db.authenticate_user("test_user", "test_password")
        self.assertIsNotNone(user)

        # Неверный пароль
        user = self.db.authenticate_user("test_user", "wrong_password")
        self.assertIsNone(user)

        # Несуществующий пользователь
        user = self.db.authenticate_user("unknown_user", "password")
        self.assertIsNone(user)

    def test_prediction_workflow(self):
        # Используем существующего пользователя
        user = self.db.get_user_by_id(self.test_user_id)

        # Пополняем баланс, чтобы хватило на оплату
        self.db.update_balance(user.id, 100.0, "Initial refill for testing")

        # Создаем задачу предсказания
        input_data = {"feature1": 1.0, "feature2": 2.0}
        task = self.db.create_prediction_task(
            user_id=user.id,
            model_name="test_model",
            input_data=input_data
        )
        self.assertIsInstance(task, PredictionTask)
        self.assertEqual(task.status, "pending")

        # Создаем результат
        predictions = {"result": 0.75}
        result = self.db.create_prediction_result(
            task_id=task.id,
            predictions=predictions,
            cost=15.0
        )
        self.assertIsInstance(result, PredictionResult)
        self.assertEqual(result.cost, 15.0)

        # Добавлено: проверка связи с задачей
        fetched_task = self.db.get_task_by_id(task.id)
        self.assertEqual(fetched_task.id, result.task_id)

        # Проверяем связь
        self.assertEqual(result.task_id, task.id)
        self.assertEqual(result.cost, 15.0)

    def tearDown(self):
        # Очищаем базу после каждого теста
        Base.metadata.drop_all(self.engine)


if __name__ == "__main__":
    unittest.main()