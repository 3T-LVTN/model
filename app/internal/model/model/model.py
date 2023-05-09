from abc import ABC, abstractmethod
import logging
from typing import Any
import pandas as pd
import numpy as np
import pickle
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sqlalchemy.orm import Session
import os

from app.adapter.file_service import file_service_adapter
from app.internal.dao.db import get_db_session
from app.internal.model.model.constants import FORMULA, PREDICTED_VAR, VC_FORMULA
from app.internal.model.model.metric import MetricsProvider, NormalMetricsProvider
from app.internal.model.model.output import Output, MosquittoNormalOutput
from app.internal.model.model.data_loader import DataLoader, WeatherDataLoader
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

    def predict(self, longitude: float, latitude: float, date_time: int, db_session: Session = None, *args, **
                kwargs) -> MosquittoNormalOutput:
        if db_session is None:
            db_session = next(get_db_session())
        inp = self.data_loader.get_history_input_data(db_session, longitude, latitude, date_time)
        model = self.get_model()
        count = model.predict(inp)
        logging.info(
            f"longitude: {longitude}, latitude: {latitude} has predict at {time_util.ts_to_datetime(date_time)} has {count}")
        return MosquittoNormalOutput(
            count=count
        )
