from datetime import datetime, time
import logging
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
from sqlalchemy import func, asc
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from app.common.constant import LOCATION_DISTANCE_THRESHOLD, PLUS, SUCCESS_STATUS_CODE
from app.common.exception import ThirdServiceException
from app.internal.dao.db import get_db_session
from app.internal.dao.predicted_var import PredictedVar
from app.internal.dao.weather_log import WeatherLog
from app.internal.dao.location import Location
from app.internal.repository.weather_log import weather_log_repo
from app.internal.model.model.constants import *
from app.internal.util.time_util import time_util
from app.adapter.visual_crossing_adapter import visual_crossing_adapter, GetWeatherRequest
from app.internal.repository.location import location_repo


class DataLoader(ABC):
    @abstractmethod
    def get_train_data(self, *args, **kwargs) -> pd.DataFrame: ...

    @abstractmethod
    def get_history_input_data(self, db_session: Session, location: Location, date_time: int, *args, **
                               kwargs) -> pd.DataFrame: ...


def get_rename_mapper_for_sqlalchemy_select(table_name: str, column_names: list[str]) -> dict[str, str]:
    return {col: col[len(table_name)+1:] for col in column_names if len(col) > len(table_name)}


class WeatherDataLoader(DataLoader):

    def preprocess_weather_log(self, db_session: Session, df: pd.DataFrame) -> pd.DataFrame:
        """handle preprocess weather log"""

        df = df.fillna(0)  # TODO: handle missing value by other way

        # ensure our id is not convert to float when load data, if remove this could lead to result in empty data frame when merge
        df = df.astype({col: "int" for col in ["time_window_id", "location_id", "date_time"]})

        for col in df.columns:
            if col not in NORMAL_COLUMNS:
                continue
            df[col] = df[col].apply(lambda x: x/np.max(df[col]) if np.max(df[col]) > 0 else 0)  # transform to 0-1 range
        return df

    def preprocess_predicted_var(self, db_session: Session, df: pd.DataFrame) -> pd.DataFrame:
        # clean column name geneate by sqlalchemy

        # ensure our id is not convert to float when load data, if remove this could lead to result in empty data frame when merge
        df = df.astype({col: "int" for col in ["time_window_id", "location_id", "date_time"]})
        return df

    def load_train_weather_log_from_db(self, db_session: Session, time_window_id: int):

        # load the data from the database into a pandas DataFrame'

        df = pd.read_sql_query(
            db_session.query(WeatherLog).filter(WeatherLog.time_window_id == time_window_id).statement,
            db_session.connection(),
            coerce_float=False
        )
        return self.preprocess_weather_log(db_session, df)

    def get_train_data(self, db_session: Session, *args,  **kwargs) -> pd.DataFrame:
        return self._get_train_data(db_session, *args, **kwargs)

    def load_predicted_var(self, db_session: Session,  time_window_id: int) -> pd.DataFrame:
        df = pd.read_sql_query(
            db_session.query(PredictedVar).filter(
                PredictedVar.time_window_id == time_window_id).statement,
            db_session.connection(),
            coerce_float=False
        )
        return self.preprocess_predicted_var(db_session, df)

    def _get_train_data(self, db_session: Session, time_window_id: int, *args,  **kwargs) -> pd.DataFrame:
        weather_log = self.load_train_weather_log_from_db(db_session, time_window_id)
        predicted_var = self.load_predicted_var(db_session, time_window_id)

        merged_df = pd.merge(
            weather_log, predicted_var, on=["time_window_id", "location_id", "date_time"], how="inner",
        )

        return merged_df[NORMAL_COLUMNS+[PREDICTED_VAR]+[RANDOM_FACTOR_COLUMN]]

    def _get_weather_log(self, db_session: Session, location: Location, date_time: int) -> WeatherLog:
        query = db_session.query(WeatherLog).where(WeatherLog.location_id == location.id,
                                                   WeatherLog.date_time == time_util.to_start_date_timestamp(date_time))
        weather_log = query.first()
        if weather_log is None:
            # if we cannot get this weather log we will try to call to visual crossing to get weather
            req = GetWeatherRequest(
                longitude=location.longitude,
                latitude=location.latitude,
                start_date_time=time_util.to_start_date_timestamp(date_time),
                end_date_time=time_util.to_end_date_timestamp(date_time),
            )
            weather_log_resp = visual_crossing_adapter.get_weather_log(req)
            if weather_log_resp.code != SUCCESS_STATUS_CODE:
                raise ThirdServiceException()
            data = weather_log_resp.data[0]
            # save it without time window id, will have celery job to update it later
            weather_log = WeatherLog(**data.dict(), location_id=location.id)
            weather_log_repo.save(db_session, weather_log)
        return weather_log

    def get_history_input_df(self, db_session: Session, weather_log: WeatherLog) -> pd.DataFrame:
        df = pd.DataFrame(weather_log.as_dict(), index=[0])
        df = self.preprocess_weather_log(db_session, df)
        return df[NORMAL_COLUMNS+[RANDOM_FACTOR_COLUMN]]

    def get_history_input_data(self, db_session: Session, location: Location, date_time: int, *args, **
                               kwargs) -> pd.DataFrame:
        '''return location id and input df for prediction'''
        weather_log = self._get_weather_log(db_session, location, date_time)

        return self.get_history_input_df(db_session, weather_log)
