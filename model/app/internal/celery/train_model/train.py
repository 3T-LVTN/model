from sqlalchemy.orm import Session

from app.internal.dao.db import get_db_session
from app.internal.model.model.model import Nb2MosquittoModel
from app.internal.dao.time_window import TimeWindow


def train_models():
    db_session = next(get_db_session())
    time_window_list = db_session.query(TimeWindow).all()
    for time_window in time_window_list:
        model = Nb2MosquittoModel(time_window.id)
        model.train(db_session)
