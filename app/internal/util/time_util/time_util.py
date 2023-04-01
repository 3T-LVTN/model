from datetime import datetime, timedelta, timezone
from typing import Optional, Union


YYYYMMDD_HHMMSS: str = '%Y-%m-%d %H:%M:%S'
YYYYMMDD_HHMMSSZ: str = '%Y-%m-%d %H:%M:%SZ'
YYYYMMDD: str = '%Y-%m-%d'
DDMMYYYY: str = '%d/%m/%Y'


def to_start_date(input_datetime: Union[datetime, None]) -> Union[datetime, None]:
    if input_datetime is None:
        return None
    return input_datetime.replace(hour=0, minute=0, second=0)


def to_start_date_timestamp(date_timestamp: int) -> int:
    return int(to_start_date(datetime.fromtimestamp(date_timestamp)).timestamp())


def to_end_date(input_datetime: datetime) -> Optional[datetime]:
    if input_datetime is None:
        return None
    return datetime(year=input_datetime.year, month=input_datetime.month, day=input_datetime.day, hour=23, minute=59, second=59)


def to_end_date_timestamp(date_timestamp: int) -> int:
    return int(to_end_date(datetime.fromtimestamp(date_timestamp)).timestamp())


def to_date(input_date: datetime, date_format: str = YYYYMMDD) -> Optional[str]:
    if input_date is None:
        return None
    return input_date.strftime(date_format)


def to_datetime(input_date: str, date_format: str = YYYYMMDD_HHMMSS) -> Optional[datetime]:
    if input_date is None:
        return None
    return datetime.strptime(input_date, date_format)


def ts_to_datetime(inp_ts: int) -> datetime:
    return datetime.fromtimestamp(inp_ts)


def datetime_to_str(inp_dt: datetime, format: str) -> str:
    return datetime.strftime(inp_dt, format)


def datetime_to_ts(inp_dt: datetime) -> int:
    return int(inp_dt.timestamp())


def ts_to_str(inp_ts: int, format: str) -> str:
    return datetime_to_str(ts_to_datetime(inp_ts), format)


def now() -> datetime:
    return datetime.now()


def utcnow() -> datetime:
    return datetime.utcnow()


def get_datetime_with_tz(inp: datetime):
    # datetime load from db has tz info  None, set it to utc
    return inp.replace(tzinfo=inp.tzinfo or timezone.utc)
