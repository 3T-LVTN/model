from fastapi_camelcase import CamelModel
from pydantic import Field


class GetWeatherSummaryRequest(CamelModel):
    location: list[str] = Field(default_factory=list)
    time_interval: int = Field(description="number of day we calculate this summary", default=7)
