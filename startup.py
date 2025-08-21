from app import create_app
from database.operations import DBOperations
from app.src.core.services import MLService
from app.src.core.models import MLModel, MLModelType

app = create_app()


# Инициализация при запуске
@app.on_event("startup")
async def startup_event():
    # Инициализация БД
    db = DBOperations()
    app.state.db = db

    # Инициализация MLService
    ml_service = MLService(db)
    ml_service.register_model(MLModel(1, "Classification", MLModelType.CLASSIFICATION, 0.5))
    ml_service.register_model(MLModel(2, "Regression", MLModelType.REGRESSION, 0.7))
    ml_service.register_model(MLModel(3, "Clustering", MLModelType.CLUSTERING, 1.0))
    app.state.ml_service = ml_service


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)