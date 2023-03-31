from datetime import datetime, time
import pandas as pd
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from app.common.constant import PLUS
from app.internal.dao.db import get_db_session
from app.internal.dao.weather_log import WeatherLog
from app.internal.dao.location import Location
from app.internal.model.model.constants import *


class DataLoader(ABC):
    @abstractmethod
    def get_train_data(self, *args, **kwargs) -> pd.DataFrame: ...
    @abstractmethod
    def get_input_data(self,  *args, **kwargs) -> pd.DataFrame: ...


class WeatherDataLoader(DataLoader):

    def preprocess_weather_log(self, db_session: Session, df: pd.DataFrame) -> pd.DataFrame:
        """handle preprocess weather log"""
        pass

    def load_weather_log_from_db(self, db_session: Session, time_window_id: int):

        # load the data from the database into a pandas DataFrame'

        df = pd.read_sql_query(
            db_session.query(WeatherLog.__tablename__).filter(WeatherLog.time_window_id == time_window_id),
            db_session
        )
        return self.preprocess_weather_log(db_session, df)

    def get_train_data(self, db_session: Session, *args,  **kwargs) -> pd.DataFrame:
        return self._get_data(db_session, *args, **kwargs)

    def _get_data(self, db_session: Session, time_window_id: int, *args,  **kwargs) -> pd.DataFrame:
        return self.load_weather_log_from_db(db_session, time_window_id)

    def get_input_data(self, db_session: Session,  longitude: float, lattitude: float, *args, **kwargs) -> pd.DataFrame:
        location_df = pd.read_sql_query(
            db_session.query(Location.__tablename__).order_by(
                asc(func.sum((Location.latitude-lattitude)**2+(Location.longitude-longitude)**2))
            ).limit(1)
        )
        return location_df
