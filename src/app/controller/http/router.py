from fastapi import APIRouter

from src.app.controller.http.health_check import srv_router
from src.app.controller.http.v1 import model_router

api_router = APIRouter(prefix="/um")
api_router.include_router(srv_router)
api_router.include_router(model_router)
