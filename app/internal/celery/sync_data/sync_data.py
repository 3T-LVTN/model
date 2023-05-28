import logging
from typing import Any
from sqlalchemy.orm import Session

from app.adapter.file_service.file_service_adapter import file_service
from app.common.constant import ALLOW_FILE_EXTENSION
from app.common.exception import MissingFieldException
from app.internal.dao.location import Location
from app.internal.dao.predicted_var import PredictedVar
from app.internal.dao.weather_log import WeatherLog
from app.internal.util.file_util.csv_reader import CsvReader
from app.internal.util.file_util.excel_reader import ExcelLoader
from app.internal.dao.db import get_db_session
from app.internal.repository.synced_file import synced_file_repo
from app.internal.dao.synced_file import SyncedFile

__SYNC_FILE_NUMBER_EXCEPTION_THRESHOLD = 10


def is_empty_field(fields: dict[str, str | Any], field_name: str):
    return fields.get(field_name) is None or len(fields.get(field_name)) == 0


def daily_sync_data_from_file_service():
    db_session = next(get_db_session)
    list_file_name = file_service.get_list_file(postfix=ALLOW_FILE_EXTENSION)
    synced_file_names = {file.file_name for file in synced_file_repo.get_all(db_session)}
    for file_name in list_file_name:
        if file_name in synced_file_names:
            continue
        sync_data_from_file(db_session, file_name)


def _write_location_to_db(db_session: Session, fields: dict[str, Any]) -> int:
    if not is_empty_field(fields=fields, field_name="lat") and not is_empty_field(fields=fields, field_name="long"):
        location = Location(
            longitude=fields.get("lat"),
            latitude=fields.get("lng"),
        )
        db_session.add(location)
        db_session.flush()
        return location.id
    return None


def _write_weather_log_to_db(db_session: Session, location_id: int, fields: dict[str, Any]):
    is_weather_log = all([not is_empty_field(fields, field_name) for field_name in WeatherLog().field_names()])
    is_weather_log = is_weather_log and not is_empty_field(fields, "date_time")
    if is_weather_log:
        db_session.add(
            WeatherLog(
                **{field_name: fields.get(field_name) for field_name in WeatherLog().field_names()},
                location_id=location_id, date_time=fields.get("date_time")))


def _write_predicted_var_to_db(db_session: Session, location_id: int,  fields: dict[str, Any]):
    if not is_empty_field(fields, "value"):
        db_session.add(
            PredictedVar(
                value=fields.get("value"),
                location_id=location_id,
                date_time=fields.get("date_time"),
            )
        )


def _write_field_to_db(db_session: Session, fields: dict[str, Any]):
    db_session.begin_nested()

    try:
        location_id = _write_location_to_db(db_session, fields)
        if location_id is None or is_empty_field(fields, "date_time"):
            raise MissingFieldException()
        _write_weather_log_to_db(db_session, location_id,  fields)
        _write_predicted_var_to_db(db_session, location_id,  fields)

    except Exception as e:
        logging.error(e)
        db_session.rollback()
    else:
        db_session.commit()
        return


def sync_data_from_file(db_session: Session, file_name: str):
    file_content = file_service.get_file_content_str(file_name)
    csv_reader = CsvReader(file_content)
    # we do not want to have our file wasted if anything occur during our tasks
    # in write field to db, we begin nested transaction
    # and commit if notthing is wrong within each row
    # rollback if that row has problem
    # after all we will commit success rows and ignore problematic rows
    exception_list: list[Exception] = []
    try:
        while True:
            try:
                fields = next(csv_reader)
                _write_field_to_db(db_session, fields)
            except StopIteration:
                if len(exception_list) == 0:
                    # if our file sync success insert synced file to db to ignore next time celery tasks start
                    db_session.add(SyncedFile(file_name=file_name))
                raise StopIteration()
            except MissingFieldException as e:
                e.file_name = file_name
                e.line = csv_reader.line_num
                exception_list.append(e)
                # if number of exception exceed our threshold, stop read file
                if len(exception_list) >= __SYNC_FILE_NUMBER_EXCEPTION_THRESHOLD:
                    raise StopIteration()
            except Exception as e:
                logging.error(e)
                exception_list.append(e)
                # if number of exception exceed our threshold, stop read file
                if len(exception_list) >= __SYNC_FILE_NUMBER_EXCEPTION_THRESHOLD:
                    raise StopIteration()
    except StopIteration:
        logging.info("read file done")
    finally:
        db_session.commit()
