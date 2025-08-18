import os
from fastapi import FastAPI
from app.src.api.routes import router
from database.operations import DBOperations

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, 'database', 'app_data.db')
DB_URL = f"sqlite:///{DB_PATH}"

@app.on_event("startup")
async def startup_event():
    app.state.db = DBOperations(db_url=DB_URL)

@app.on_event("shutdown")
async def shutdown_event():
    pass

app.include_router(router)