from sqlalchemy.orm import Session

from app.adapter.file_service.file_service_adapter import file_service
from app.internal.util.file_util.csv_reader import CsvReader
from app.internal.util.file_util.excel_reader import ExcelLoader
from app.internal.dao.db import get_db_session
from app.internal.repository.synced_file import synced_file_repo
from app.internal.dao.synced_file import SyncedFile


def daily_sync_data_from_file_service():
    db_session = next(get_db_session)
    list_file_name = file_service.get_list_file()
    synced_file_names: tuple[str] = (file.file_name for file in synced_file_repo.get_all(db_session))
    for file_name in list_file_name:
        if file_name in synced_file_names:
            continue
        sync_data_from_file(db_session, file_name)


def sync_data_from_file(db_session: Session, file_name: str):
    file_content = file_service.get_file_content(file_name)
    csv_reader = CsvReader()

    csv_reader.dialect
