from celery.utils.log import get_task_logger

from app.internal.celery.celery import celery_app
from app.internal.celery.base import BaseTask
from app.internal.celery.crawl_weather_data.crawl_weather_data import get_data
from app.internal.dao.db import get_db_session
from app.internal.celery.train_model.train import train_models

logger = get_task_logger(__name__)


@celery_app.task(name='task_crawl_weather_data', base=BaseTask)
def task_crawl_data():
    logger.info('Running crawl weather data')
    get_data(db_session=next(get_db_session()))


@celery_app.task(name='task_train_model', base=BaseTask)
def task_train_model():
    logger.info('Start trainning all model')
    train_models()
