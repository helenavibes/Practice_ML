import unittest
from database.operations import DBOperations
from database.models import User, Base
import bcrypt
from sqlalchemy import create_engine


class TestDBOperations(unittest.TestCase):
    def setUp(self):
        # Создаем временную базу в памяти
        self.engine = create_engine('sqlite:///:memory:')
        # Создаем таблицы с помощью Base из models
        Base.metadata.create_all(self.engine)

        # Передаем созданный engine в DBOperations
        self.db = DBOperations(engine=self.engine)

        # Создаем тестового пользователя и сразу получаем его ID
        self.test_user_id = self.db.create_user(
            username="test_user",
            email="test@example.com",
            password="test_password"
        ).id  # Сохраняем ID сразу после создания

    def test_create_user(self):
        # Получаем пользователя заново
        user = self.db.get_user_by_username("test_user")
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(bcrypt.checkpw(
            "test_password".encode('utf-8'),
            user.password_hash
        ))

    def test_update_balance(self):
        # Пополнение баланса
        transaction = self.db.update_balance(self.test_user_id, 300.0, "Test deposit")
        self.assertEqual(transaction.amount, 300.0)

        # Получаем пользователя заново для проверки баланса
        user = self.db.get_user_by_username("test_user")
        self.assertEqual(user.balance, 300.0)

        # Списание средств
        self.db.update_balance(self.test_user_id, -100.0, "Test withdrawal")
        user = self.db.get_user_by_username("test_user")
        self.assertEqual(user.balance, 200.0)

    def test_transaction_history(self):
        self.db.update_balance(self.test_user_id, 200.0, "First transaction")
        self.db.update_balance(self.test_user_id, -50.0, "Second transaction")

        history = self.db.get_transaction_history(self.test_user_id)
        self.assertEqual(len(history), 2)
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

    def tearDown(self):
        # Очищаем базу после каждого теста
        Base.metadata.drop_all(self.engine)


if __name__ == "__main__":
    unittest.main()