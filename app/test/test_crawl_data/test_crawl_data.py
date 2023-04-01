import unittest
from unittest.mock import patch
from sqlalchemy.orm import Session
from datetime import datetime
import codecs
from app.adapter.base import BaseResponse
from app.common.constant import SUCCESS_STATUS_CODE
from app.common.exception import ThirdServiceException

from app.internal.celery.crawl_weather_data.crawl_weather_data import get_data
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.weather_log import WeatherLog
from app.internal.dao.location import Location
from app.adapter.visual_crossing_adapter import VisualCrossingAdapter

_mock_data = [
    "Address,Date time,Minimum Temperature,Maximum Temperature,Temperature,Dew Point,Relative Humidity,Heat Index,Wind Speed,Wind Gust,Wind Direction,Wind Chill,Precipitation,Precipitation Cover,Snow Depth,Visibility,Cloud Cover,Sea Level Pressure,Weather Type,Latitude,Longitude,Resolved Address,Name,Info,Conditions",
    '"27.581094,-82.554803","04/25/2011",69.5,85.7,76.4,68.0,76.58,89.4,12.6,23.0,136.75,,0.0,0.0,0.0,9.9,16.6,1016.0,"Thunderstorm",27.581094,-82.554803,"27.581094,-82.554803","27.581094,-82.554803","","Clear"'
]


class TestCrawlData:

    def test_crawl_success(self, db_session_test: Session):
        mock_resp = patch.object(
            VisualCrossingAdapter, "get", side_effect=lambda * args, **
            kwargs: BaseResponse(code=SUCCESS_STATUS_CODE, data=codecs.iterencode(_mock_data, encoding="utf-8")))
        mock_resp.start()
        db_session_test.add(TimeWindow(
            sliding_size=1,
            start_ts=int(datetime(year=2011, month=4, day=24).timestamp()),
            end_ts=int(datetime(year=2011, month=4, day=26).timestamp())
        ))
        db_session_test.add(Location(
            longitude=27.581094,
            latitude=-82.554803
        ))
        db_session_test.commit()
        get_data(db_session_test)
        mock_resp.stop()
        weather_log = db_session_test.query(WeatherLog).all()
        assert len(weather_log) == 2
        assert weather_log[0].date_time is not None

    def test_crawl_failed(self, db_session_test: Session):
        mock_resp = patch.object(
            VisualCrossingAdapter, "get", side_effect=lambda * args, **
            kwargs: BaseResponse(code=500))
        mock_resp.start()
        db_session_test.add(TimeWindow(
            sliding_size=1,
            start_ts=int(datetime(year=2011, month=4, day=24).timestamp()),
            end_ts=int(datetime(year=2011, month=4, day=26).timestamp())
        ))
        db_session_test.add(Location(
            longitude=27.581094,
            latitude=-82.554803
        ))
        db_session_test.commit()
        try:
            get_data(db_session_test)
        except Exception as e:
            assert isinstance(e, ThirdServiceException)
