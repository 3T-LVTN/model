import codecs
from datetime import datetime
from unittest.mock import patch
from app.adapter.base import BaseResponse
from app.common.constant import SUCCESS_STATUS_CODE
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
        try:
            _mock_data = '''Address,Date time,Minimum Temperature,Maximum Temperature,Temperature,Dew Point,Relative Humidity,Heat Index,Wind Speed,Wind Gust,Wind Direction,Wind Chill,Precipitation,Precipitation Cover,Snow Depth,Visibility,Cloud Cover,Sea Level Pressure,Weather Type,Latitude,Longitude,Resolved Address,Name,Info,Conditions
        "27.581094,-82.554803","04/25/2011",69.5,85.7,76.4,68.0,76.58,89.4,12.6,23.0,136.75,,0.0,0.0,0.0,9.9,16.6,1016.0,"Thunderstorm",27.581094,-82.554803,"27.581094,-82.554803","27.581094,-82.554803","","Clear"
        '''
            mock_resp = patch.object(
                VisualCrossingAdapter, "get", side_effect=lambda * args, **
                kwargs: BaseResponse(code=SUCCESS_STATUS_CODE, data=codecs.encode(_mock_data, encoding="utf-8")))
            mock_resp.start()

            model = Nb2MosquittoModel(1)
            a = model.predict(27.581094, -82.554803, 1452186000)
            print(a)
        finally:
            mock_resp.stop()
