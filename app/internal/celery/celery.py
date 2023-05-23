import kombu.serialization
from app.config import env_var
from app.common.util.json import json_encode, json_decode
from app.internal.celery.crawl_weather_data.crawl_weather_data import get_data
from datetime import timedelta
import logging
import sys

from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

_task_logger = get_task_logger(__name__)


kombu.serialization.register(
    name='service-json',
    encoder=json_encode,
    decoder=json_decode,
    content_type='application/service-json',
    content_encoding='utf-8'
)


def make_celery():
    celery = Celery(
        __name__,
        backend=env_var.CELERY_RESULT_BACKEND,
        broker=env_var.CELERY_BROKER_URL,
        include=[]
    )
    celery.conf.update(
        task_serializer='service-json',
        accept_content=['service-json', ],
        result_serializer='service-json',
        task_acks_late=True,
    )

    # Define a task to run when Celery starts

    @celery.task()
    def on_connect():
        _task_logger.info('Celery started!')

    # Connect the task to the after_configure signal

    @celery.on_after_configure.connect
    def setup_periodic_tasks(sender, **kwargs):
        from app.internal.celery.tasks import task_crawl_data
        sender.add_periodic_task(10.0, task_crawl_data.s(), name='crawl_data')

    celery.autodiscover_tasks(['app.internal.celery.tasks.task_crawl_data'])
    celery.autodiscover_tasks(['app.internal.celery.tasks.task_train_model'])
    celery.autodiscover_tasks(['app.internal.celery.tasks.task_sync_data_from_s3'])
    # For config schedule cronjob
    celery.conf.update(
        beat_schedule={
            'task_crawl_data': {
                'task': 'task_crawl_data',
                'schedule': crontab(minute=0, hour='0')
            }
        },
    )
    return celery
    # Define a task to run when Celery starts


celery_app = make_celery()
