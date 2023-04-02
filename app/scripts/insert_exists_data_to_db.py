from app.internal.dao.weather_log import WeatherLog
from app.internal.util.file_util import excel_reader
from openpyxl import Workbook, load_workbook
import csv
from openpyxl.cell.cell import Cell
from datetime import datetime
from openpyxl.styles import Font, PatternFill
from openpyxl.worksheet.worksheet import Worksheet
from sqlalchemy.orm import Session
from app.internal.repository.weather_log import weather_log_repo
from app.internal.dao.location import Location
from app.internal.repository.location import LocationFilter, location_repo
from app.internal.dao.time_window import TimeWindow
from app.internal.dao.predicted_var import PredictedVar
from app.internal.repository.predicted_var import predicted_var_repo
from app.internal.repository.time_window import time_window_repo, TimeWindowFilter
from app.common.constant import COMMA
from app.internal.util.time_util import time_util


def insert_exists_weather_data(db_session: Session):
    with open('app/test/sample/long_lat_data.csv') as f:
        csv_reader = csv.reader(f, delimiter=COMMA)
        rows = list(csv_reader)
        headers: list[str]
        min_ts: int = 10e10
        max_ts: int = -1
        for idx, row in enumerate(rows):
            if idx == 0:
                headers = row
                idx += 1
                continue
            data_dict = dict(zip(headers, row))
            info = data_dict.pop("info")
            if info.lower().strip().strip('"') == "No data available".lower():
                continue
            date_time = datetime.strptime(data_dict.pop("date_time").strip('"'), r'%m/%d/%Y')
            min_ts = min(time_util.datetime_to_ts(time_util.to_start_date(date_time)), min_ts)
            max_ts = max(time_util.datetime_to_ts(time_util.to_end_date(date_time)), max_ts)
        filter = TimeWindowFilter(
            eq_start_date_ts=min_ts,  # filter min ts is in the same date with that time window start ts
            eq_end_date_ts=max_ts    # filter max ts is in the same date with that time window end ts
        )
        time_window = time_window_repo.get_first(db_session, filter)
        if time_window is None:
            time_window = time_window_repo.save(db_session, TimeWindow(sliding_size=1, start_ts=min_ts, end_ts=max_ts))
        for idx, row in enumerate(rows):
            if idx == 0:
                headers = row
                idx += 1
                continue
            data_dict = dict(zip(headers, row))
            info = data_dict.pop("info")
            if info.lower().strip().strip('"') == "No data available".lower():
                continue
            longitude = data_dict.pop("longitude")
            latitude = data_dict.pop("latitude")
            location = location_repo.get_first(
                db_session, filter=LocationFilter(longitude=float(longitude), latitude=float(latitude)))
            if location is None:
                location = location_repo.save(db_session, Location(longitude=longitude, latitude=latitude))
            date_time = date_time = time_util.to_start_date(
                datetime.strptime(data_dict.pop("date_time").strip('"'), r'%m/%d/%Y'))
            data_dict.update({"date_time": date_time})
            weather_log_model = WeatherLog(**data_dict, location_id=location.id, time_window_id=time_window.id)
            weather_log_repo.save(db_session, weather_log_model)


def insert_table_s2_predicted_var_to_db(db_session: Session):
    with open('app/test/sample/Table_S2.csv') as f:
        csv_reader = csv.reader(f, delimiter=COMMA)
        rows = list(csv_reader)
        headers: list[str]
        min_ts: int = 10e10
        max_ts: int = -1
        for idx, row in enumerate(rows):
            if idx == 0:
                headers = row
                idx += 1
                continue
            data_dict = dict(zip(headers, row))
            genus = data_dict.pop("genus")
            if "Culex".lower() not in genus.lower().strip().strip('"'):
                continue
            date_time = datetime.strptime(data_dict.pop("date").strip('"'), r'%Y-%m-%d')
            min_ts = min(time_util.datetime_to_ts(time_util.to_start_date(date_time)), min_ts)
            max_ts = max(time_util.datetime_to_ts(time_util.to_end_date(date_time)), max_ts)
        filter = TimeWindowFilter(
            eq_start_date_ts=min_ts,  # filter min ts is in the same date with that time window start ts
            eq_end_date_ts=max_ts    # filter max ts is in the same date with that time window end ts
        )
        time_window = time_window_repo.get_first(db_session, filter)
        if time_window is None:
            time_window = time_window_repo.save(db_session, TimeWindow(
                sliding_size=1, start_ts=min_ts, end_ts=max_ts))
        for idx, row in enumerate(rows):
            if idx == 0:
                headers = row
                idx += 1
                continue
            data_dict = dict(zip(headers, row))
            genus = data_dict.pop("genus")
            if "Culex".lower() not in genus.lower().strip().strip('"'):
                continue
            value_str = data_dict.pop("abundance")
            try:
                value = int(value_str)
            except:
                continue
            longitude = data_dict.pop("long")
            latitude = data_dict.pop("lat")
            location = location_repo.get_first(
                db_session, filter=LocationFilter(longitude=float(longitude), latitude=float(latitude)))
            if location is None:
                location = location_repo.save(db_session, Location(longitude=longitude, latitude=latitude))
            date_time = time_util.to_start_date(
                datetime.strptime(data_dict.pop("date").strip('"'), r'%Y-%m-%d'))
            data_dict.update({"date_time": date_time})

            predicted_var = PredictedVar(value=value, date_time=date_time,
                                         location_id=location.id, time_window_id=time_window.id)
            predicted_var_repo.save(db_session, predicted_var)
