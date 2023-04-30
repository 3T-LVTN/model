from datetime import datetime
from app.internal.celery.crawl_weather_data.crawl_weather_data import get_data
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.weather_log import WeatherLog
from app.internal.dao.location import Location
from app.adapter.visual_crossing_adapter import VisualCrossingAdapter
from app.internal.util.time_util import time_util
from app.scripts.insert_exists_data_to_db import insert_exists_weather_data, insert_table_s2_predicted_var_to_db
from app.internal.celery.train_model.train import train_models
from app.internal.model.model.model import Nb2MosquittoModel


class TestScripts:

    def test_scripts_insert_weather_log(self, db_session_test):
        insert_exists_weather_data(db_session=db_session_test)

    def test_scripts_insert_predicted_var(self, db_session_test):
        insert_table_s2_predicted_var_to_db(db_session_test)

    def test_train(self):
        train_models()

    def test_predict(self):
        model = Nb2MosquittoModel(1)
        a = model.predict(27.581094, -82.554803, 1452186000)
        print(a)
