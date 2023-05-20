from fastapi_camelcase import CamelModel
from pydantic import Field

from app.api.response.base import BaseResponse


class SummaryLocationInfo(CamelModel):
    location_code: str
    lat: float
    lng: float
    value: float
    precip: float
    temperature: float


class GetWeatherSummaryResponse(BaseResponse):
    data: list[SummaryLocationInfo] = Field(default_factory=list)
