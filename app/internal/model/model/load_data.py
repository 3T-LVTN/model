from datetime import datetime, time
import pandas as pd
import numpy as np
import pickle
import statsmodels.api as sm
import statsmodels.formula.api as smf
from sqlalchemy.orm import Session


from app.common.constant import PLUS
from app.internal.dao.db import get_db_session
from app.internal.dao.weather_log import WeatherLog
from app.internal.model.model.constants import *
from app.internal.model.model.metric import get_custom_metrics


def preprocess_weather_log(db_session: Session, df: pd.DataFrame) -> pd.DataFrame:
    """handle preprocess weather log"""
    pass


def get_alpha_constants(df: pd.DataFrame) -> float:
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


def load_weather_log_from_db(time_window_id: int):
    db_session = next(get_db_session())

    # load the data from the database into a pandas DataFrame
    df = pd.read_sql_table(WeatherLog.__tablename__, db_session)
    process_df = preprocess_weather_log(db_session, df)

    alpha = get_alpha_constants(process_df)

    # fit the GLMM using the mixedlm function from the statsmodels library
    model = sm.MixedLM.from_formula(
        FORMULA, df, groups=process_df[RANDOM_FACTOR_COLUMN],
        family=sm.families.NegativeBinomial(alpha=alpha))
    metric = get_custom_metrics()
    result = model.fit_regularized(eval_func=metric)

    result_file = f"{OUTPUT_MODEL_FOLDER}/model_{time_window_id}_{int(datetime.timestamp(datetime.now()))}.pkl"
    with open(result_file, "w+") as f:
        pickle.dump(result, f)
