from abc import ABC, abstractmethod
from typing import Any
import pandas as pd
import numpy as np
import pickle
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sqlalchemy.orm import Session
import os

from app.internal.dao.db import get_db_session
from app.internal.model.model.constants import FORMULA, PREDICTED_VAR, RANDOM_FACTOR_COLUMN, OUTPUT_MODEL_FOLDER
from app.internal.model.model.metric import MetricsProvider, NormalMetricsProvider
from app.internal.model.model.output import Output, MosquittoNormalOutput
from app.internal.model.model.data_loader import DataLoader, WeatherDataLoader


class Model(ABC):

    @property
    @abstractmethod
    def data_loader(self) -> DataLoader: ...

    @property
    @abstractmethod
    def metrics_provider(self) -> MetricsProvider: ...

    @property
    @abstractmethod
    def file_path(self) -> str: ...

    # function
    @abstractmethod
    def train(self, *args, **kwargs): ...

    @abstractmethod
    def predict(self,  *args, **kwargs) -> Output: ...

    def load_model(self):
        if not os.path.isfile(self.file_path):
            return None
        with open(self.file_path, 'rb') as f:
            # Load the pickled object
            self.model = pickle.load(f)

    def get_model(self):
        if self.model is None:
            return self.train()
        return self.model


class Nb2MosquittoModel(Model):
    data_loader = WeatherDataLoader()
    metrics_provider = NormalMetricsProvider()
    time_window_id: int
    file_path: str
    model: sm.MixedLM = None

    def __init__(self, time_window_id: int) -> None:
        super().__init__()
        self.time_window_id = time_window_id
        self.file_path = f"{OUTPUT_MODEL_FOLDER}/time_window_id.pkl"
        self.load_model()

    def get_model(self) -> sm.MixedLM:
        return super().get_model()

    def get_alpha_constants(self, df: pd.DataFrame) -> float:
        # TODO: refactor this function, cannot typehint for model and result so we just accept it colorless
        # some string constant below is math symbol and just has meaning in this specific function so i dont think we should declare constant for them
        poisson = sm.MixedLM(FORMULA, df, family=sm.families.Poisson()).fit()

        df["LAMBDA"] = poisson.mu
        df['AUX_OLS_DEP'] = df.apply(lambda x: ((x[PREDICTED_VAR] - x['LAMBDA'])
                                                ** 2 - x['LAMBDA']) / x['LAMBDA'], axis=1)

        # use patsy to form the model specification for the OLSR
        ols_expr = """AUX_OLS_DEP ~ LAMBDA - 1"""

        # Configure and fit the OLSR model
        aux_olsr_results = smf.ols(ols_expr, df).fit()
        return aux_olsr_results.params[0]

    def train(self, db_session: Session = None, is_force=False) -> Any:

        if not is_force and self.model is not None:
            # if not force to retrain, we return current model if has
            return self.model

        if db_session is None:
            db_session = next(get_db_session())
        df = self.data_loader.get_train_data(db_session)

        model = sm.MixedLM.from_formula(
            FORMULA, df, groups=df[RANDOM_FACTOR_COLUMN],
            family=sm.families.NegativeBinomial(alpha=self.get_alpha_constants(df)))

        metric = self.metrics_provider.get_custom_metrics()

        result = model.fit_regularized(eval_func=metric)

        with open(self.file_path, "w+"):
            result.save(self.file_path)

        return result

    def predict(self, longitude: float, lattitude: float, db_session: Session = None, *args, **kwargs) -> MosquittoNormalOutput:
        if db_session is None:
            db_session = next(get_db_session())
        inp = self.data_loader.get_input_data(db_session, longitude, lattitude)
        model = self.get_model()
        return MosquittoNormalOutput(
            count=model.predict(inp)
        )
