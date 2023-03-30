
from app.internal.dao.time_window import TimeWindow
from app.internal.repository.base import BaseRepo


class TimeWindowRepo(BaseRepo):
    pass


time_window_repo = TimeWindowRepo(TimeWindow)
