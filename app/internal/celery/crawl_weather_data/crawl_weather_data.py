import logging

from uuid import uuid1
from datetime import timedelta, datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.common.constant import SUCCESS_STATUS_CODE
from app.common.exception import ThirdServiceException


from app.internal.dao.db import get_db_session
from app.internal.dao.location import Location
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.weather_log import WeatherLog
from app.internal.repository.location import location_repo
from app.internal.repository.time_window import time_window_repo
from app.internal.repository.weather_log import WeatherLogFilter, weather_log_repo
from app.adapter.visual_crossing_adapter import visual_crossing_adapter, GetWeatherRequest
from app.internal.celery.crawl_weather_data.constants import *

_logger = logging.getLogger(__name__)


def gen_get_weather_request(
        lat: float, long: float, start_date_ts: int, end_date_ts: int) -> GetWeatherRequest:
    start_date = datetime.fromtimestamp(start_date_ts)
    end_date = datetime.fromtimestamp(end_date_ts)
    return GetWeatherRequest(
        longitude=long,
        latitude=lat,
        start_date_time=start_date.strftime(DATE_FORMAT),
        end_date_time=end_date.strftime(DATE_FORMAT),
    )


def get_weather_log_model(time_window: TimeWindow, location: Location) -> WeatherLog:

    req = gen_get_weather_request(location.latitude, location.longitude,
                                  time_window.start_ts, time_window.end_ts)
    resp = visual_crossing_adapter.get_weather_log(req)
    if resp.code != SUCCESS_STATUS_CODE:
        raise ThirdServiceException()
    return WeatherLog(**resp.data.__dict__, location_id=location.id, time_window_id=time_window.id)


def get_data(db_session: Session):
    _logger.info("start get data")
    query = db_session.query(TimeWindow).where(TimeWindow.sliding_size.__eq__(1))
    time_windows: list[TimeWindow] = time_window_repo.get_all(db_session, query)
    locations: list[Location] = location_repo.get_all(db_session)

    weather_log_repo.get_all(db_session, )

    for time_window in time_windows:
        for location in locations:
            # check if exists this weather log
            weather_log = db_session.query(WeatherLog).filter(
                WeatherLog.location_id == location.id,
                WeatherLog.time_window == time_window.id
            ).first()

            # if not exists crawl data
            if weather_log is None:
                weather_log = get_weather_log_model(time_window, location)
                # write new data to csv
                db_session.add(weather_log)
                db_session.commit()
