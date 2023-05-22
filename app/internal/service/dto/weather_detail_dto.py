from dataclasses import dataclass

from app.internal.dao.weather_log import WeatherLog


@dataclass
class WeatherDetailDTO:
    lat: float
    long: float
    location_code: str
    map_date_to_prediction_value: dict[int, float] = None
    map_date_to_weather_log: dict[int, WeatherLog] = None
