from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
import enum
from datetime import datetime
import bcrypt

Base = declarative_base()


class MLModelType(enum.Enum):
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"

class TransactionType(enum.Enum):
    DEPOSIT = "deposit"
    PREDICTION_FEE = "prediction_fee"
    ADMIN_REFILL = "admin_refill"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(128), nullable=False)
    balance = Column(Float, default=0.0)

    def check_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password.encode('utf-8')
        )

    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class Transaction(Base):
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    amount = Column(Float, nullable=False)
    transaction_type = Column(Enum(TransactionType), nullable=False)  # Исправлено: тип Enum
    timestamp = Column(DateTime, default=datetime.utcnow)
    description = Column(String)

class PredictionTask(Base):
    __tablename__ = 'prediction_tasks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    model_name = Column(String, nullable=False)
    input_data = Column(JSON, nullable=False)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    result = relationship("PredictionResult", uselist=False, back_populates="task")

class PredictionResult(Base):
    __tablename__ = 'prediction_results'
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('prediction_tasks.id'), nullable=False)
    predictions = Column(JSON, nullable=False)
    cost = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    task = relationship("PredictionTask", back_populates="result")