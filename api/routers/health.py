from fastapi import APIRouter
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    Returns the status of the API service.
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        service="Used Cars API"
    )


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Used Cars API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }
