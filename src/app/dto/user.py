import typing as t

from datetime import datetime
from uuid import UUID

from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

from src.app.dto.base_orm import BaseORMModel

phone_number = PhoneNumber
phone_number.default_region_code = "+7"


class UserDTO(BaseORMModel):
    username: str
    email: EmailStr
    phone: phone_number


class UserCreate(UserDTO):
    pass


class UserUpdate(UserDTO):
    pass


class SingleUserResponse(UserDTO):
    id: UUID  # noqa: A003
    created_at: datetime
    updated_at: datetime
    deleted_at: t.Optional[datetime]
