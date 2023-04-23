import os
import socket
from typing import Callable, Generator
from unittest.mock import patch
import pytest
from redis import Redis
import sqlalchemy.engine
from app.config import env_var
from app.internal.dao.base import Base
from app.internal.dao.db import get_db_session
from app.main import app, celery_app
from sqlalchemy import create_engine, text
from sqlalchemy.orm import session, sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database
from starlette.testclient import TestClient
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer


def get_random_free_port():
    sock = socket.socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


def init_db_container() -> PostgresContainer:
    db_container = PostgresContainer(
        'postgres:latest',
        user=env_var.DB_USERNAME,
        password=env_var.DB_PASSWORD,
        dbname=env_var.DB_NAME,
    )
    # Monkey-patch the get_container_host_ip method due to windows error
    db_container.get_container_host_ip = lambda: 'localhost'
    db_container.with_bind_ports(env_var.DB_PORT, get_random_free_port())  # bind db port with other port to run test
    db_container.start()

    return db_container


def init_redis() -> str:
    # init redis container for celery
    redis_container = RedisContainer()
    redis_container.get_container_host_ip = lambda: 'localhost'
    redis_container.with_bind_ports(env_var.REDIS_PORT, get_random_free_port()).start()

    return redis_container.get_client()


# def init_test():
#     # init test db container
#     init_db_container()


def get_test_db_session(test_engine: sqlalchemy.engine.Engine) -> Callable[[], Generator[session.Session, None, None]]:
    def get_db_session():
        db_test_session_maker = sessionmaker(
            autocommit=False, autoflush=False, bind=test_engine
        )
        db_test_session = db_test_session_maker()
        try:
            yield db_test_session
        finally:
            db_test_session.close()
    return get_db_session


# db_container = init_db_container()
# db_uri: str = db_container.get_connection_url()
db_uri = env_var.DB_URI
test_engine = create_engine(db_uri)


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    """
    Create a clean database on every test case.

    We use the `sqlalchemy_utils` package here for a few helpers in consistently
    creating and dropping the database.
    """
    from app.adapter.base import BaseAdapter, BaseResponse
    # mock this so when we run test we wont be spam with noti
    mock_adapter = patch.object(BaseAdapter, attribute="_get_response",
                                side_effect=lambda *args, **kwargs: BaseResponse(code=200, data={}))
    mock_adapter.start()
    app.dependency_overrides[
        get_db_session
    ] = get_test_db_session(test_engine)  # Mock the Database Dependency
    yield  # Run the tests.
    # drop_database(db_uri)  # Drop the test database.


# @pytest.fixture(autouse=True)
# def mock_db_session(request):
#     db_test_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=get_test_db_engine())
#     db_session_test = db_test_session_maker()
#     db_mock = patch('app.dao.db.db.get_db_session', side_effect=lambda: iter([db_session_test]))
#     db_session_maker_mock = patch('app.dao.db.db.DBSession', side_effect=db_test_session_maker)
#     db_mock.start()
#     db_session_maker_mock.start()
#     yield
#     db_session_maker_mock.stop()
#     db_mock.stop()
#     db_session_test.close()

# @pytest.fixture(scope="session", autouse=True)
# def create_test_celery():
#     redis_url = init_redis()

#     # redis_conn_kw = redis_client.get_connection_kwargs()
#     # redis_host = redis_conn_kw.get("host")
#     # redis_port = redis_conn_kw.get("port")
#     # redis_url = f"redis://{redis_host}:{redis_port}"

#     celery_app.conf.update(task_always_eager=True,
#                            broker_url=redis_url,
#                            result_backend=redis_url)


@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'amqp://',
        'result_backend': 'redis://'
    }


@pytest.fixture()
def db_session_test():
    """Returns an sqlalchemy session, and after the test tears down everything properly."""

    db_session_maker = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db_session_test = db_session_maker()

    yield db_session_test
    # put back the connection to the connection pool
    db_session_test.close()
