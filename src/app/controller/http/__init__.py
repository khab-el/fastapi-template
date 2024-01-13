from src.app.controller.http.router import api_router
from src.app.controller.http.health_check import srv_router

__all__ = (
    "srv_router",
    "api_router",
)
