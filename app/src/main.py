import os
import sys
import json
import logging
from datetime import datetime
from flask import Blueprint, jsonify, request
from database.operations import DBOperations
from database.models import MLModelType
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Fix BASE_DIR path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

# Blueprint
bp = Blueprint('routes', __name__)

# DB setup
DB_PATH = os.path.join(BASE_DIR, 'database', 'app_data.db')
DB_URL = f"sqlite:///{DB_PATH}"
db = DBOperations(db_url=DB_URL)

# Available ML models
ML_MODELS = {
    "classification": {"cost_per_request": 0.5, "description": "Classification model"},
    "regression": {"cost_per_request": 0.7, "description": "Regression model"},
    "clustering": {"cost_per_request": 1.0, "description": "Clustering model"}
}

@bp.route('/')
def status():
    return jsonify({
        "status": "running",
        "message": "ML Prediction Service",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    })

@bp.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@bp.route('/models')
def list_models():
    return jsonify({"models": ML_MODELS, "count": len(ML_MODELS)}), 200

@bp.route('/register', methods=['POST'])
def register_user():
    data = request.json or {}
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    if not (username and email and password):
        return jsonify({"error": "Missing required fields"}), 400
    try:
        user = db.create_user(username, email, password)
        return jsonify({
            "message": "User created",
            "user_id": user.id,
            "username": user.username,
            "email": user.email
        }), 201
    except SQLAlchemyError as e:
        logger.error(f"Registration error: {e}")
        return jsonify({"error": "Registration failed"}), 400

@bp.route('/login', methods=['POST'])
def login_user():
    data = request.json or {}
    user = db.authenticate_user(data.get('username', ''), data.get('password', ''))
    if not user:
        return jsonify({"error": "Invalid credentials"}), 401
    return jsonify({
        "message": "Login successful",
        "user_id": user.id,
        "username": user.username,
        "balance": user.balance
    }), 200

@bp.route('/user/<int:user_id>/balance', methods=['GET'])
def get_balance(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"user_id": user.id, "username": user.username, "balance": user.balance}), 200

@bp.route('/user/<int:user_id>/deposit', methods=['POST'])
def deposit_funds(user_id):
    data = request.json or {}
    amount = data.get('amount')
    if amount is None or amount <= 0:
        return jsonify({"error": "Invalid amount"}), 400
    try:
        user = db.get_user_by_id(user_id)
        if not user:
            return jsonify({"error": "User not found"}), 404
        txn = db.update_balance(user_id, amount, data.get('description', 'Deposit'))
        return jsonify({
            "message": "Deposit successful",
            "new_balance": db.get_user_by_id(user_id).balance,
            "transaction_id": txn.id
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Deposit error: {e}")
        return jsonify({"error": "Deposit failed"}), 400

@bp.route('/user/<int:user_id>/history', methods=['GET'])
def get_transaction_history(user_id):
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    history = db.get_transaction_history(user_id)
    return jsonify({
        "user_id": user_id,
        "transactions": [{
            "id": tx.id,
            "amount": tx.amount,
            "type": tx.transaction_type.value,
            "description": tx.description,
            "timestamp": tx.timestamp.isoformat()
        } for tx in history],
        "count": len(history)
    }), 200

@bp.route('/predict', methods=['POST'])
def predict():
    data = request.json or {}
    user_id = data.get('user_id')
    model_name = data.get('model_name')
    input_data = data.get('input_data')
    if not (user_id and model_name and isinstance(input_data, list)):
        return jsonify({"error": "Missing or invalid fields"}), 400
    if model_name not in ML_MODELS:
        return jsonify({"error": "Model not available"}), 404
    user = db.get_user_by_id(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    cost = ML_MODELS[model_name]['cost_per_request'] * len(input_data)
    if user.balance < cost:
        return jsonify({"error": "Insufficient funds", "required": cost, "balance": user.balance}), 402

    try:
        task = db.create_prediction_task(user_id, model_name,
                                         MLModelType[model_name.upper()],
                                         json.dumps(input_data), cost)
        predictions = [f"pred_{model_name}_{i}" for i in range(len(input_data))]
        result = db.create_prediction_result(task.id, json.dumps(predictions), cost)
        db.update_balance(user_id, -cost, f"Prediction fee for {model_name}")

        return jsonify({
            "task_id": task.id,
            "result_id": result.id,
            "predictions": predictions,
            "cost": cost,
            "new_balance": db.get_user_by_id(user_id).balance
        }), 200
    except SQLAlchemyError as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": "Prediction failed"}), 500

@bp.route('/task/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = db.get_prediction_task(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
    return jsonify({
        "task_id": task.id,
        "status": task.status,
        "model_name": task.model_name,
        "input_data": json.loads(task.input_data),
        "predictions": json.loads(task.predictions) if task.predictions else None,
        "cost": task.cost,
        "created_at": task.created_at.isoformat()
    }), 200

@bp.route('/result/<int:result_id>', methods=['GET'])
def get_result(result_id):
    result = db.get_prediction_task(result_id)
    if not result:
        return jsonify({"error": "Result not found"}), 404
    return jsonify({
        "result_id": result.id,
        "predictions": json.loads(result.predictions),
        "cost": result.cost,
        "timestamp": result.created_at.isoformat()
    }), 200