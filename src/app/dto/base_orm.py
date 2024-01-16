from pydantic import BaseModel


class BaseORMModel(BaseModel):
    class Config:
        orm_mode = True
