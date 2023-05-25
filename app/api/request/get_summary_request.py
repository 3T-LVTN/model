from fastapi_camelcase import CamelModel
from pydantic import Field


class Location(CamelModel):
    lat: float = None
    lng: float = None
    location_code: str = None


class GetWeatherSummaryRequest(CamelModel):
    locations: list[Location] = Field(default_factory=list)
    time_interval: int = Field(description="number of day we calculate this summary", default=7)
