import codecs
from typing import Any
from fastapi_camelcase import CamelModel
from pydantic import Json
import json
import re
from app.adapter.base import BaseAdapter, BaseResponse
from app.common.constant import COMMA, DOUBLE_QUOTE, SUCCESS_STATUS_CODE, UNDERSCORE, WHITE_SPACE
from app.config.secret import API_KEY_GENERATOR


_URL = r'https://weather.visualcrossing.com'
_NAME = "visual crossing"
_GET_WEATHER_LOG_END_POINT = r"VisualCrossingWebServices/rest/services/weatherdata/history"
TIME_DELTA = 1


NOT_COMMA_OR_DOUBLE_QUOTE = r'[^,"]'
STRING_INSIDE_DOUBLE_QUOTE = r'"[^"]*"'
COMMA_OUTSIDE_OF_DOUBLE_QUOTE_PATTERN = r'(?:[^,"]|"(?:[^"])*")*'


class GetWeatherRequest(CamelModel):
    longitude: str
    latitude: str
    start_date_time: str
    end_date_time: str
    key: str = None


class _GetWeatherRequest(CamelModel):
    location: str = None
    start_date_time: str = None
    end_date_time: str = None
    key: str = None
    aggregate_hours: int = 24

    def __init__(self, req: GetWeatherRequest):
        super().__init__()
        self.location = f"{req.latitude},{req.longitude}"
        self.start_date_time = req.start_date_time
        self.end_date_time = req.end_date_time


class GetWeatherLogResponseData:
    address: str
    date_time: str
    minimum_temperature: str
    maximum_temperature: str
    temperature: str
    dew_point: str
    relative_humidity: str
    heat_index: str
    wind_speed: str
    wind_gust: str
    wind_direction: str
    wind_chill: str
    precipitation: str
    precipitation_cover: str
    snow_depth: str
    visibility: str
    cloud_cover: str
    sea_level_pressure: str
    weather_type: str
    latitude: str
    longitude: str
    resolved_address: str
    name: str
    info: str
    conditions: str


class GetWeatherLogResponse(BaseResponse):
    data: GetWeatherLogResponseData

    def __init__(self, base_resp: BaseResponse) -> None:
        super().__init__()
        self.code = base_resp.code
        self.message = base_resp.message


class VisualCrossingAdapter(BaseAdapter):

    def __init__(self, url: str, name: str) -> None:
        super().__init__(url, name)
        self.current_key = next(API_KEY_GENERATOR)

    def _clean_header(self, header: str) -> list[str]:
        data_field_list = header.split(COMMA)
        # transform header to snake case
        return [data_field.strip().lower().replace(WHITE_SPACE, UNDERSCORE) for data_field in data_field_list]

    def _clean_resp(self, content: str) -> list[str]:

        data_list: list[str] = re.findall(COMMA_OUTSIDE_OF_DOUBLE_QUOTE_PATTERN, content)
        return [data.strip() for data in data_list]

    def _clean_resp_data(self, data: Any) -> GetWeatherLogResponseData:
        content = codecs.iterdecode(data, 'utf-8')
        # TODO: improve performance by run in parralel below
        resp_header = self._clean_header(next(content))
        resp_content = self._clean_resp(next(content))
        data = GetWeatherLogResponseData()
        data.__dict__ = dict(zip(resp_header, resp_content))
        return data

    def get_weather_log(self, req: GetWeatherRequest) -> GetWeatherLogResponse:
        req = _GetWeatherRequest(req)
        base_resp = self.get(end_point=_GET_WEATHER_LOG_END_POINT, **req.dict())
        resp = GetWeatherLogResponse(base_resp)

        if base_resp.code != SUCCESS_STATUS_CODE:
            # if base resp is not success we might run out of api key quota
            try:
                # try to get next key
                self.current_key = next(API_KEY_GENERATOR)
            except StopIteration:
                # if stop iteration mean we run out of api key, try again next day
                return resp
            return self.get_weather_log(req)

        resp.data = self._clean_resp_data(base_resp.data)
        return resp


visual_crossing_adapter = VisualCrossingAdapter(name=_NAME, url=_URL)
