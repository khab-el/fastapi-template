import datetime
import logging

from fastapi import APIRouter, Request

from src.app.dto import ErrorResponse
from src.app.modules.calc_score import calc_score_func

log = logging.getLogger(__name__)

model_router = APIRouter(
    tags=["score"],
    # include_in_schema=False,
)


@model_router.get(
    "/score",
    status_code=200,
    responses={502: {"model": ErrorResponse}},
)
async def calc_score(
    request: Request,
    inn: str,
    kpp: str,
    sign_date: datetime.date,
):
    """Calc score router.

    :param request: _description_
    :type request: Request
    :param inn: _description_
    :type inn: str
    :param kpp: _description_
    :type kpp: str
    :param sign_date: _description_
    :type sign_date: datetime.date
    :return: _description_
    :rtype: _type_
    """
    return calc_score_func(inn=inn, kpp=kpp, sign_date=sign_date)
