from dataclasses import dataclass
from typing import Any

from app.internal.dao.location import Location
from app.internal.dao.third_party_location import ThirdPartyLocation
from app.internal.dao.weather_log import WeatherLog


@dataclass
class WeatherSummaryDTO:
    map_location_id_to_weather_log: dict[int, WeatherLog]
    map_location_id_to_prediction: dict[int, float]
    map_location_id_to_third_party: dict[int, ThirdPartyLocation]
    map_location_id_to_location: dict[int, Location]
