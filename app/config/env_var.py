import os
from typing import Dict, Any

# APP
HOST = "0.0.0.0"
APP_PORT = 8000

# DB
DB_HOST: str = os.getenv("DB_HOST", default="localhost")
DB_PORT: str = os.getenv("DB_PORT", default="5432")
DB_NAME: str = os.getenv("DB_NAME", default="vove")
DB_USERNAME: str = os.getenv("DB_USERNAME", default="root")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", default="123456")
DB_URI: str = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:' \
    f'{DB_PORT}/{DB_NAME}'


# REDIS
REDIS_HOST: str = os.getenv("CELERY_HOST", default="localhost")
REDIS_PORT: str = os.getenv("CELERY_PORT", default="6379")
REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"
CACHE_OUTDATED_TIME: int = int(os.getenv('CALCULATION_CONFIG_CACHE_OUTDATED_TIME', default=600))
# CELERY
# default celery broker and result back end host = redis url
CELERY_BROKER_URL: str = REDIS_URL
CELERY_RESULT_BACKEND: str = REDIS_URL

# LOGGER
LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
}


# SLACK
# list of mention users for notification in slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", default="")
ENVIRONMENT = os.getenv("ENVIRONMENT", default="DEVELOP")
SLACK_ALERT_CHANNEL_NAME = os.getenv("SLACK_ALERT_CHANNEL", default="hoethy")
