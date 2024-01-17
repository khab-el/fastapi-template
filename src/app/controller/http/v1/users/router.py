import logging

from fastapi import APIRouter, Request
from pydantic.json_schema import SkipJsonSchema

from src.app.dto import SingleUserResponse, UserCreate
from src.app.entity import User

log = logging.getLogger(__name__)

users_router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@users_router.get(
    "/",
    status_code=200,
)
async def get_users(request: Request) -> list[SingleUserResponse | SkipJsonSchema[None]]:
    """ping."""
    res = await User.get_all(request.state.db_session)
    return res


@users_router.post(
    "/",
    status_code=201,
)
async def create_user(request: Request, user: UserCreate) -> SingleUserResponse:
    """ping."""
    res = await User(**user.model_dump()).save(request.state.db_session)
    return res
