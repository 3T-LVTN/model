from fastapi_camelcase import CamelModel
from pydantic import Field
from datetime import datetime, timedelta


class GetWeatherDetailRequest(CamelModel):
    start_time: int = Field(default_factory=lambda: datetime.now().timestamp())   # timestamp
    end_time: int = Field(default_factory=lambda: (datetime.now()-timedelta(days=7)).timestamp())
    lat: float = None
    lng: float = None
    # time_interval: int = Field(default=1, description="number of day we between 2 response record") # TODO: support later
    location_code: str = Field(description="currently is ward code")
