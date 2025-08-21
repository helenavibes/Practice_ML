from database.operations import DBOperations
from database.models import TransactionType

db = DBOperations()

def init():
    # Демо пользователь
    try:
        demo_user = db.create_user("demo_user", "demo@example.com", "demo123")
        db.update_balance(demo_user.id, 100.0, "Initial deposit", TransactionType.ADMIN_REFILL)
        print(f"Created demo user: {demo_user.username}")
    except Exception as e:
        print(f"User creation failed: {e}")

    # Демо админ
    try:
        admin_user = db.create_user("admin", "admin@example.com", "admin123")
        db.update_balance(admin_user.id, 1000.0, "Admin initial credit", TransactionType.ADMIN_REFILL)
        print(f"Created admin: {admin_user.username}")
    except Exception as e:
        print(f"Admin creation failed: {e}")

    # Можно расширить, добавив базовые ML модели (если есть отдельная таблица)

if __name__ == "__main__":
    init()