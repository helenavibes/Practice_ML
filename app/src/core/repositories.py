from .models import User, Transaction, TransactionType
from typing import Optional, List

class UserRepository:
    def get_user_by_credentials(self, username: str, password_hash: str) -> Optional[User]:
        pass

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        pass

class TransactionRepository:
    def log_transaction(self, user_id: int, amount: float, transaction_type: TransactionType) -> None:
        pass

    def get_user_history(self, user_id: int) -> List[Transaction]:
        pass