from fastapi import APIRouter

from api.schemas import HealthResponse


router = APIRouter()


@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "healthy",
        "service": "narrate-iq",
        "version": "0.1.0",
    }
