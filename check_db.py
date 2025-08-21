from database.operations import DBOperations


def main():
    db = DBOperations()

    # Проверим демо-пользователей
    admin = db.get_user_by_username("admin_demo")
    user = db.get_user_by_username("user_demo")

    print(f"Admin: {admin.username}, Balance: {admin.balance}")
    print(f"User: {user.username}, Balance: {user.balance}")

    # Проверим историю транзакций пользователя
    transactions = db.get_transaction_history(user.id)
    print(f"\nTransaction history for {user.username}:")
    for t in transactions:
        print(f"{t.timestamp} | {t.transaction_type} | {t.amount} | {t.description}")


if __name__ == "__main__":
    main()