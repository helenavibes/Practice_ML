from .models import Base, User, Transaction
from .operations import DBOperations
import bcrypt
from sqlalchemy.orm import Session

def init_database():
    db = DBOperations()
    Base.metadata.create_all(db.engine)

    with Session(db.engine) as session:
        # Создаем администратора
        admin = session.query(User).filter_by(username="admin_demo").first()
        if not admin:
            hashed_password = bcrypt.hashpw("admin_password".encode('utf-8'), bcrypt.gensalt())
            admin = User(
                username="admin_demo",
                email="admin@example.com",
                password_hash=hashed_password,
                is_admin=True
            )
            session.add(admin)
            session.commit()
            session.refresh(admin)
            print("Admin created.")

        # Создаем обычного пользователя
        user = session.query(User).filter_by(username="user_demo").first()
        if not user:
            hashed_password = bcrypt.hashpw("user_password".encode('utf-8'), bcrypt.gensalt())
            user = User(
                username="user_demo",
                email="user@example.com",
                password_hash=hashed_password
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            print("User created.")

        # Демо-транзакции
        def add_transaction(user_obj, amount, description):
            user_obj.balance += amount
            transaction_type = "deposit" if amount > 0 else "withdrawal"
            transaction = Transaction(
                user_id=user_obj.id,
                amount=amount,
                transaction_type=transaction_type,
                description=description
            )
            session.add(transaction)

        add_transaction(admin, 1000.0, "Initial admin bonus")
        add_transaction(user, 500.0, "Welcome bonus")
        add_transaction(user, -150.0, "Purchase: Groceries")
        add_transaction(user, 300.0, "Deposit from bank")

        session.commit()

    print("Database initialized with demo data!")

if __name__ == "__main__":
    init_database()