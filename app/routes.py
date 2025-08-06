from flask import Flask, jsonify, request
from src.core.models import MLModelType, MLModel
from src.core.services import MLService

app = Flask(__name__)

# Инициализация сервиса
ml_service = MLService()

# Регистрация моделей при запуске
ml_service.register_model(
    MLModel(1, "Classification Model", MLModelType.CLASSIFICATION, 0.5)
)
ml_service.register_model(
    MLModel(2, "Regression Model", MLModelType.REGRESSION, 0.7)
)
ml_service.register_model(
    MLModel(3, "Clustering Model", MLModelType.CLUSTERING, 1.0)
)

@app.route('/')
def status():
    return jsonify({
        "status": "running",
        "message": "ML Service is ready",
        "models": [model.name for model in ml_service._MLService__models.values()]
    })

@app.route('/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

@app.route('/models')
def list_models():
    models = []
    for model in ml_service._MLService__models.values():
        models.append({
            "id": model.model_id,
            "name": model.name,
            "type": model.model_type.value,
            "cost": model.cost_per_request
        })
    return jsonify(models)

@app.route('/predict/<int:model_id>', methods=['POST'])
def predict(model_id: int):
    # Заглушка для обработки предсказаний
    return jsonify({
        "model_id": model_id,
        "status": "processing",
        "message": "Prediction request received",
        "input_data": request.json.get('data', [])
    }), 202