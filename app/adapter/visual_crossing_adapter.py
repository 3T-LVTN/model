import codecs
from datetime import timedelta, datetime
from typing import Any
from fastapi_camelcase import CamelModel
from pydantic import Json
import json
import re
from app.adapter.base import BaseAdapter, BaseResponse
from app.common.constant import COMMA, DOUBLE_QUOTE, SUCCESS_STATUS_CODE, UNDERSCORE, WHITE_SPACE
from app.config.secret import API_KEY_GENERATOR
from app.internal.util.time_util import time_util

_URL = r'https://weather.visualcrossing.com'
_NAME = "visual crossing"
_GET_WEATHER_LOG_END_POINT = r"VisualCrossingWebServices/rest/services/weatherdata/history"
_DATE_TIME_FORMAT = "%Y-%m-%d"
_RESP_DATE_TIME_FORMAT = r'%m/%d/%Y'
_TIME_DELTA = 1


NOT_COMMA_OR_DOUBLE_QUOTE = r'[^,"]'
STRING_INSIDE_DOUBLE_QUOTE = r'"[^"]*"'
COMMA_OUTSIDE_OF_DOUBLE_QUOTE_PATTERN = r'\s*,\s*(?=(?:[^"]*"[^"]*")*[^"]*$)'


class GetWeatherRequest(CamelModel):
    longitude: str = None
    latitude: str = None
    start_date_time: int = None
    end_date_time: int = None
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
        self.start_date_time = time_util.ts_to_str(req.start_date_time, _DATE_TIME_FORMAT)
        self.end_date_time = time_util.ts_to_str(req.end_date_time, _DATE_TIME_FORMAT)


class GetWeatherLogResponseData(CamelModel):
    address: str = None
    date_time: datetime = None
    minimum_temperature: str = None
    maximum_temperature: str = None
    temperature: str = None
    dew_point: str = None
    relative_humidity: str = None
    heat_index: str = None
    wind_speed: str = None
    wind_gust: str = None
    wind_direction: str = None
    wind_chill: str = None
    precipitation: str = None
    precipitation_cover: str = None
    snow_depth: str = None
    visibility: str = None
    cloud_cover: str = None
    sea_level_pressure: str = None
    weather_type: str = None
    latitude: str = None
    longitude: str = None
    resolved_address: str = None
    name: str = None
    info: str = None
    conditions: str = None


class GetWeatherLogResponse(BaseResponse):
    data: list[GetWeatherLogResponseData] = None


class VisualCrossingAdapter(BaseAdapter):

    def __init__(self, url: str, name: str) -> None:
        super().__init__(url, name)
        self.current_key = next(API_KEY_GENERATOR)

    def _clean_header(self, header: str) -> list[str]:
        data_field_list = header.split(COMMA)
        # transform header to snake case
        return [data_field.strip().lower().replace(WHITE_SPACE, UNDERSCORE) for data_field in data_field_list]

    def _format_resp(self, content: str) -> list[str]:

        data_list: list[str] = re.split(COMMA_OUTSIDE_OF_DOUBLE_QUOTE_PATTERN, content)
        return [data.strip() for data in data_list]

    def _format_resp_data(self, data: Any) -> GetWeatherLogResponseData:
        content = codecs.iterdecode(data, 'utf-8')
        # TODO: improve performance by run in parralel below
        resp_header = self._clean_header(next(content))
        resp_content = self._format_resp(next(content))
        resp_dict = dict(zip(resp_header, resp_content))
        date_time = resp_dict.pop("date_time").strip('"')
        resp_dict.update({"date_time": datetime.strptime(date_time, _RESP_DATE_TIME_FORMAT)})
        resp = GetWeatherLogResponseData(**resp_dict)

        return resp

    def _prepare_list_request(self, req: GetWeatherRequest) -> list[_GetWeatherRequest]:
        '''
        we will split an request to a list of multiple request with time delta = 1 because we only have limited api quota per day
        it would be wasted if one of our request using 1000 query and cause some error
        '''
        start_date_ts = req.start_date_time
        end_date_ts = req.end_date_time

        list_req: list[_GetWeatherRequest] = []
        while start_date_ts < end_date_ts:
            start_date_dt = time_util.ts_to_datetime(start_date_ts)  # convert to datetime to add time delta
            _end_date_ts = time_util.datetime_to_ts(
                start_date_dt+timedelta(_TIME_DELTA))  # convert current request end date
            req.end_date_time = _end_date_ts  # overide current req
            list_req.append(_GetWeatherRequest(req))
            start_date_ts = _end_date_ts  # override start date ts with current end date ts

        return list_req

    def get_single_weather_log_data(self, req: _GetWeatherRequest) -> GetWeatherLogResponse:
        base_resp = self.get(end_point=_GET_WEATHER_LOG_END_POINT, params=req)
        if base_resp.code == SUCCESS_STATUS_CODE:
            data = self._format_resp_data(base_resp.data)
            return GetWeatherLogResponse(code=base_resp.code, message=base_resp.message, data=[data])

        # retry in case we run out of api key
        try:
            # try to get next key
            self.current_key = next(API_KEY_GENERATOR)
        except StopIteration:
            # if stop iteration mean we run out of api key, return empty success code so we stop and save record to db
            return GetWeatherLogResponse(code=SUCCESS_STATUS_CODE, data=[])
        # retry this req
        req.key = self.current_key
        base_resp = self.get(end_point=_GET_WEATHER_LOG_END_POINT, params=req)
        if base_resp.code == SUCCESS_STATUS_CODE:
            data = self._format_resp_data(base_resp.data)
            return GetWeatherLogResponse(code=base_resp.code, message=base_resp.message, data=[data])
        else:
            return GetWeatherLogResponse(**base_resp.dict())

    def get_weather_log(self, base_req: GetWeatherRequest) -> GetWeatherLogResponse:
        req_list = self._prepare_list_request(base_req)
        resp = GetWeatherLogResponse()
        resp.data = []
        for req in req_list:
            req.key = self.current_key
            single_resp = self.get_single_weather_log_data(req)
            if single_resp.code != SUCCESS_STATUS_CODE:
                return GetWeatherLogResponse(**single_resp.dict())
            resp.data.extend(single_resp.data)
        resp.code = SUCCESS_STATUS_CODE
        return resp


visual_crossing_adapter = VisualCrossingAdapter(name=_NAME, url=_URL)
