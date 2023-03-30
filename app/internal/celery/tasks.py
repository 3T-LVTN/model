from celery.utils.log import get_task_logger

from app.internal.celery.celery import celery_app
from app.internal.celery.crawl_weather_data.crawl_weather_data import get_data
from app.internal.dao.db import get_db_session

logger = get_task_logger(__name__)


@celery_app.task(name='crawl_weather_data')
def task_crawl_data():
    logger.info('Running crawl weather data')
    get_data(db_session=next(get_db_session()))
