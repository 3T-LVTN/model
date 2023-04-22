from typing import Any
from fastapi_camelcase import CamelModel

from app.common.constant import SUCCESS_STATUS_CODE, SUCCESS_STATUS_MSG


class BaseResponse(CamelModel):
    class Config:
        anystr_strip_whitespace = True
    # errro msg will be handle in error handler
    code: int = SUCCESS_STATUS_CODE
    message: str = SUCCESS_STATUS_MSG
    data: Any = None
