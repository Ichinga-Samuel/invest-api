from typing import Optional
from datetime import datetime, timedelta
from functools import wraps, partial

from pydantic import BaseModel, Field
from tortoise.timezone import localtime, make_aware, now as nw


class ResponseModel(BaseModel):
    status: bool = True
    message: str


class HttpExceptionResponse(ResponseModel):
    headers: Optional[dict]
    status = False


class RequestValidationErrorResponse(ResponseModel):
    detail: list
    body: dict
    status = False
    message = "Fix the following validation errors"


class Token(BaseModel):
    access_token: str = Field(..., alias="accessToken")
    token_type: str = Field('bearer', alias="tokenType")


def now():
    return make_aware(datetime.now())


def error_handler(func=None, error=None):
    if func is None:
        return partial(error_handler, error=error)

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as err:
            err = error or "something went wrong"
            return ResponseModel(message=err, status=False)

    return wrapper
