from app.internal.dao.base import Page
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.predicted_var import PredictedVar
from app.internal.repository.base import BaseRepo

from sqlalchemy.orm import Session, Query
from pydantic import BaseModel


class PredictedVarRepo(BaseRepo[PredictedVar]):
    ...


predicted_var_repo = PredictedVarRepo(PredictedVar)
