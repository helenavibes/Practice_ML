from fastapi import FastAPI
from app.src.api.routes import router

def create_app():
    app = FastAPI()
    app.include_router(router)
    return app