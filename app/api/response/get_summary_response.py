from fastapi_camelcase import CamelModel
from pydantic import Field

from app.api.response.base import BaseResponse
from app.api.response.common import Rate


class SummaryLocationInfo(CamelModel):
    location_code: str
    lat: float
    lng: float
    value: float
    precip: float
    temperature: float
    rate: Rate


class GetWeatherSummaryResponse(BaseResponse):
    data: list[SummaryLocationInfo] = Field(default_factory=list)
