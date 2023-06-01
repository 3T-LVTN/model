from fastapi_camelcase import CamelModel
from pydantic import Field

from app.api.response.base import BaseResponse, Geometry
from app.api.response.common import Rate


class LocationDetail(CamelModel):
    date: int = Field(None, description="date of that location detail")
    value: float = None
    temperature: float = None
    precip: float = None
    rate: Rate = None


class LocationDetailGeometry(Geometry):
    location_code: str = None


class LocationDetailData(CamelModel):
    location_geometry: LocationDetailGeometry = None
    location_detail: list[LocationDetail] = Field(default_factory=list)


class GetWeatherDetailResponse(BaseResponse):
    data: LocationDetailData = None
