from app.internal.celery.crawl_weather_data.crawl_weather_data import get_data
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.weather_log import WeatherLog
from app.internal.dao.location import Location
from app.adapter.visual_crossing_adapter import VisualCrossingAdapter
from app.scripts.insert_exists_data_to_db import insert_exists_weather_data, insert_table_s2_predicted_var_to_db


class TestScripts:

    def test_scripts_insert_weather_log(self, db_session_test):
        insert_exists_weather_data(db_session=db_session_test)

    def test_scripts_insert_predicted_var(self, db_session_test):
        insert_table_s2_predicted_var_to_db(db_session_test)
