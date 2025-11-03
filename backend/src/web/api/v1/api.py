from fastapi import APIRouter
from src.web.api.v1.endpoints.management import router as management_router

api_router = APIRouter()
api_router.include_router(management_router)