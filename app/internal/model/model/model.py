from abc import ABC, abstractmethod
from datetime import timedelta
import datetime
import logging
from typing import Any
import pandas as pd
import numpy as np
import pickle
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sqlalchemy.orm import Session
from sqlalchemy import func, asc, desc

from app.adapter.file_service import file_service_adapter
from app.common.constant import LOCATION_DISTANCE_THRESHOLD
from app.internal.dao.db import get_db_session
from app.internal.dao.location import Location
from app.internal.dao.predicted_log import PredictedLog
from app.internal.model.model.constants import FORMULA, PREDICTED_VAR, VC_FORMULA
from app.internal.model.model.metric import MetricsProvider, NormalMetricsProvider
from app.internal.model.model.output import Output, MosquittoNormalOutput
from app.internal.model.model.data_loader import DataLoader, WeatherDataLoader
from app.internal.repository.location import LocationRepo, location_repo
from app.internal.repository.predicted_log import PredictedLogFilter, predicted_log_repo
from app.internal.util.time_util import time_util


class Model(ABC):

    file_path: str

    @property
    @abstractmethod
    def data_loader(self) -> DataLoader: ...

    @property
    @abstractmethod
    def metrics_provider(self) -> MetricsProvider: ...

    # function

    @abstractmethod
    def train(self, *args, **kwargs): ...

    @abstractmethod
    def predict(self,  *args, **kwargs) -> Output: ...

    def load_model(self):
        if self.model is not None:
            return
        logging.info(f"model file path {self.file_path}")
        # try to load model
        try:
            logging.info(self.file_path)
            data = file_service_adapter.file_service.get_file_content(self.file_path)
            self.model = pickle.loads(data)
            logging.info("load model success")
        except EOFError:
            return

    def get_model(self):
        self.load_model()
        # if try to load model still result in None
        if self.model is None:
            logging.info("model is None start train model")
            self.train()
        return self.model

    def save(self, model: Any):
        self.model = model
        file_service_adapter.file_service.upload_file(pickle.dumps(self.model), self.file_path)


class Nb2MosquittoModel(Model):
    data_loader = WeatherDataLoader()
    metrics_provider = NormalMetricsProvider()
    time_window_id: int
    file_path: str
    model: sm.BinomialBayesMixedGLM = None

    def __init__(self, time_window_id: int) -> None:
        super().__init__()
        self.time_window_id = time_window_id
        self.file_path = f"model/{time_window_id}.pkl"
        self.load_model()

    def get_model(self) -> sm.MixedLM:
        return super().get_model()

    def get_alpha_constants(self, df: pd.DataFrame) -> float:
        # TODO: refactor this function, cannot typehint for model and result so we just accept it colorless
        # some string constant below is math symbol and just has meaning in this specific function so i dont think we should declare constant for them
        poisson = sm.GLM(
            df[PREDICTED_VAR],
            df[[col for col in df.columns if str(col) != PREDICTED_VAR]],
            family=sm.families.Poisson()).fit()

        train_df = df.copy()
        train_df["LAMBDA"] = poisson.mu
        train_df['AUX_OLS_DEP'] = train_df.apply(lambda x: ((x[PREDICTED_VAR] - x['LAMBDA'])
                                                            ** 2 - x['LAMBDA']) / x['LAMBDA'], axis=1)

        # use patsy to form the model specification for the OLSR
        ols_expr = """AUX_OLS_DEP ~ LAMBDA - 1"""

        # Configure and fit the OLSR model
        aux_olsr_results = smf.ols(ols_expr, train_df).fit()
        return aux_olsr_results.params[0]

    def train(self, db_session: Session = None, is_force=False) -> Any:

        if not is_force and self.model is not None:
            # if not force to retrain, we return current model if has
            return self.model

        if db_session is None:
            db_session = next(get_db_session())
        df = self.data_loader.get_train_data(db_session, self.time_window_id)

        alpha = self.get_alpha_constants(df)

        model = sm.PoissonBayesMixedGLM.from_formula(
            formula=FORMULA, data=df, vc_formulas=VC_FORMULA,
            vcp_p=alpha,
        )
        model.family = sm.families.NegativeBinomial(alpha=alpha)

        result = model.fit_map()
        self.save(result)
        return result

    def _get_nearest_location(self, db_session: Session, longitude: float, latitude: float) -> Location:
        logging.info("start getting nearest location base on long lat")
        max_lng = longitude+LOCATION_DISTANCE_THRESHOLD
        min_lng = longitude-LOCATION_DISTANCE_THRESHOLD
        max_lat = latitude + LOCATION_DISTANCE_THRESHOLD
        min_lat = latitude-LOCATION_DISTANCE_THRESHOLD
        distances = func.abs(Location.longitude - longitude) + func.abs(Location.latitude - latitude)
        location = db_session.query(Location).where(
            Location.longitude < max_lng,
            Location.longitude > min_lng,
            Location.latitude < max_lat,
            Location.latitude > min_lat,
        ).order_by(asc(distances)).first()

        return location

    def get_input_location(self, db_session: Session, longitude: float, latitude: float) -> Location:
        logging.info("start getting input location")
        location = self._get_nearest_location(db_session, longitude, latitude)
        if location is None:
            # if there is no location is valid
            location = Location(longitude=longitude, latitude=latitude)
            location_repo.save(db_session, location)
        return location

    def predict(
            self, longitude: float, latitude: float, date_time: int, db_session: Session = None,
            *args, **kwargs) -> MosquittoNormalOutput:
        location = self.get_input_location(db_session, longitude, latitude)
        logging.info(f"location id base on long {longitude} lat {latitude} is: {location.id}")
        return self.get_predict_with_location_model(location=location, date_time=date_time, db_session=db_session)

    def predict_with_location_id(
            self, *, location_id: int, date_time: int, db_session: Session) -> MosquittoNormalOutput:
        location = location_repo.get_by_id(db_session, location_id)
        return self.get_predict_with_location_model(location=location, date_time=date_time, db_session=db_session)

    def get_predict_with_location_model(
            self, location: Location, date_time: int, db_session: Session) -> MosquittoNormalOutput:
        history_predict = predicted_log_repo.first(
            db_session,
            filter=PredictedLogFilter(
                location_id=location.id,
                created_at_lt=time_util.datetime_to_ts(time_util.now()),
                created_at_gt=time_util.to_start_date(time_util.now()).timestamp(),
            )
        )
        logging.info(
            f"history prediction for location id {location.id} at {date_time} is {history_predict.value if history_predict is not None else 'None'}")
        if history_predict is not None:
            return MosquittoNormalOutput(
                count=history_predict.value
            )
        inp = self.data_loader.get_history_input_data(db_session, location, date_time)
        model = self.get_model()
        count = model.predict(inp)

        predicted_log_repo.save(
            db_session,
            PredictedLog(
                location_id=location.id,
                value=count[0],
                model_file_path=self.file_path,
                predict_time=time_util.to_start_date_timestamp(date_time),
            )
        )
        logging.info(
            f"new prediction for location id {location.id} at {date_time} is {count}")
        return MosquittoNormalOutput(
            count=count
        )

    def predict_for_time_interval(
            self, location_id: int, start_time: int, end_time: int, db_session: Session) -> list[float]:

        start_time_dt = time_util.ts_to_datetime(start_time)
        time_interval = time_util.ts_to_datetime(end_time) - time_util.ts_to_datetime(start_time)
        res: list[float] = []
        for i in range(time_interval.days):
            res.append(
                self.predict_with_location_id(
                    location_id=location_id, date_time=time_util.datetime_to_ts(
                        start_time_dt + datetime.timedelta(days=i)),
                    db_session=db_session).count)

        return res
