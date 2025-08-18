from fastapi import APIRouter

router = APIRouter(tags=["Health"])

@router.get("/")
def root():
    return {"message": "ML Service is running"}

@router.get("/health")
def health():
    return {"status": "ok"}