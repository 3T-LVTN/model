from fastapi_camelcase import CamelModel
from pydantic import Field

from app.api.response.base import BaseResponse, Geometry


class LocationDetail(CamelModel):
    date: int = Field(description="date of that location detail")
    value: float
    temperature: float
    precip: float


class LocationDetailGeometry(Geometry):
    location_code: str = None


class LocationDetailData(CamelModel):
    location_geometry: LocationDetailGeometry
    location_detail: list[LocationDetail] = Field(default_factory=list)


class GetWeatherDetailResponse(BaseResponse):
    data: LocationDetailData = None
