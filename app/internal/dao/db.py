import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, session

from app.config import env_var

engine_options = {
    "max_overflow": 0,
}
engine = create_engine(
    env_var.DB_URI, pool_pre_ping=True, echo=None, **engine_options
)  # Set time zone UTC
DBSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session() -> Generator[session.Session, None, None]:
    '''always use get db session instead normal way to get session as this function will handle close'''
    try:
        db_session = DBSession()
        yield db_session
    finally:
        db_session.close()
