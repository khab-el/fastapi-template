from pydantic import BaseModel


class BaseORMModel(BaseModel):
    class Config:
        from_attributes = True
