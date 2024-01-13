import logging

from fastapi import APIRouter, Request

from src.app.dto import ErrorResponse
from src.app.entity import User

log = logging.getLogger(__name__)

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@users_router.get(
    "/",
    status_code=200,
    responses={502: {"model": ErrorResponse}},
)
async def get_users(request: Request):
    """ping."""
    res = await User.get_all(request.state.db_session)
    return res
