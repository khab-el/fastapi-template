from fastapi import APIRouter

from src.app.controller.http.v1 import v1_router

api_router = APIRouter()
api_router.include_router(v1_router)
