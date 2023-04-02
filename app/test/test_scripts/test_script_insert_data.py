from app.internal.celery.crawl_weather_data.crawl_weather_data import get_data
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.weather_log import WeatherLog
from app.internal.dao.location import Location
from app.adapter.visual_crossing_adapter import VisualCrossingAdapter
from app.scripts.insert_exists_data_to_db import insert_exists_weahter_data


class TestScripts:

    def test_scripts(self, db_session_test):
        insert_exists_weahter_data(db_session=db_session_test)
