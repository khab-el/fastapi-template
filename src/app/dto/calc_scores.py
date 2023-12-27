import datetime

from pydantic import BaseModel, validator


class CalcRequest(BaseModel):
    inn: str
    kpp: str
    sign_date: datetime.date
    
    @validator("sign_date", pre=True)
    def parse_birthdate(cls, value):
        return datetime.datetime.strptime(
            value,
            "%Y/%m/%d"
        ).date()
