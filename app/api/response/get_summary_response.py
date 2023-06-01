from fastapi_camelcase import CamelModel
from pydantic import Field

from app.api.response.base import BaseResponse
from app.api.response.common import Rate


class SummaryLocationInfo(CamelModel):
    location_code: str = None
    lat: float = None
    lng: float = None
    value: float = None
    precip: float = None
    temperature: float = None
    rate: Rate = None


class GetWeatherSummaryResponse(BaseResponse):
    data: list[SummaryLocationInfo] = Field(default_factory=list)
