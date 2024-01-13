from fastapi import APIRouter

from src.app.controller.http.v1.users.router import users_router

v1_router = APIRouter(prefix="/v1")
v1_router.include_router(users_router)

__all__ = ("v1_router",)
