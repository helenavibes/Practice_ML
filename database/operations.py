from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import User, Transaction
import bcrypt
import os


class DBOperations:
    def __init__(self, db_url=None, engine=None):
        if engine:
            self.engine = engine
        else:
            if db_url is None:
                db_path = os.path.join(os.path.dirname(__file__), 'app_data.db')
                db_url = f'sqlite:///{db_path}'
            self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)

    def hash_password(self, password):
        # Генерируем соль и хешируем пароль
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)

    def verify_password(self, password, hashed_password):
        # Проверяем пароль с сохраненным хешем
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)

    def create_user(self, username, email, password, is_admin=False):
        session = self.Session()
        try:
            new_user = User(
                username=username,
                email=email,
                password_hash=self.hash_password(password),
                is_admin=is_admin
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)  # Обновляем объект для получения ID
            return new_user
        finally:
            session.close()

    def update_balance(self, user_id, amount, description=""):
        session = self.Session()
        try:
            user = session.get(User, user_id)
            if not user:
                raise ValueError(f"User with ID {user_id} not found")

            user.balance += amount
            transaction_type = "deposit" if amount > 0 else "withdrawal"

            new_transaction = Transaction(
                user_id=user_id,
                amount=amount,
                transaction_type=transaction_type,
                description=description
            )
            session.add(new_transaction)
            session.commit()
            session.refresh(new_transaction)
            session.expunge(new_transaction)
            return new_transaction
        finally:
            session.close()

    def get_transaction_history(self, user_id):
        session = self.Session()
        try:
            return session.query(Transaction).filter_by(user_id=user_id).order_by(Transaction.timestamp.desc()).all()
        finally:
            session.close()

    def get_user_by_username(self, username):
        session = self.Session()
        try:
            return session.query(User).filter_by(username=username).first()
        finally:
            session.close()

    def get_user_by_id(self, user_id):
        session = self.Session()
        try:
            return session.query(User).get(user_id)
        finally:
            session.close()

    def authenticate_user(self, username, password):
        user = self.get_user_by_username(username)
        if user and self.verify_password(password, user.password_hash):
            return user
        return None