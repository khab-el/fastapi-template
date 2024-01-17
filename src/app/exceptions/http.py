from pydantic import BaseModel


class ApiError(BaseModel):
    message: str


class ApiExceptionResponse(BaseModel):
    success: bool = False
    errors: list[ApiError]


class ApiValidationError(ApiError):
    field: str


class ApiInvalidResponse(BaseModel):
    success: bool = False
    errors: list[ApiValidationError]
