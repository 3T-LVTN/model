from app.internal.dao.synced_file import SyncedFile
from app.internal.dao.time_window import TimeWindow
from app.internal.repository.base import BaseRepo


class SyncedFileRepo(BaseRepo[SyncedFile]):
    ...


synced_file_repo = SyncedFileRepo(SyncedFile)
