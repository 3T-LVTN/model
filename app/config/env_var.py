import json
import os
from typing import Dict, Any

# APP
HOST = "0.0.0.0"
APP_PORT = 8000

# DB
DB_HOST: str = os.getenv("DB_HOST", default="172.17.0.1")
DB_PORT: str = os.getenv("DB_PORT", default="5005")
DB_NAME: str = os.getenv("DB_NAME", default="vove")
DB_USERNAME: str = os.getenv("POSTGRES_USER", default="postgres")
DB_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", default="thinh3112001")
DB_URI: str = f'postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:' \
    f'{DB_PORT}/{DB_NAME}'


# REDIS
REDIS_HOST: str = os.getenv("REDIS_HOST", default="172.17.0.1")
REDIS_PORT: str = os.getenv("REDIS_PORT", default="6379")
REDIS_URL: str = f"redis://{REDIS_HOST}:{REDIS_PORT}"
CACHE_OUTDATED_TIME: int = int(os.getenv('CALCULATION_CONFIG_CACHE_OUTDATED_TIME', default=600))
# CELERY
# default celery broker and result back end host = redis url
CELERY_BROKER_URL: str = REDIS_URL
CELERY_RESULT_BACKEND: str = REDIS_URL

# LOGGER
LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
        },
        "generic": {
            "format": "%(levelname)-10.10s %(asctime)s [%(name)s][%(module)s:%(lineno)d] %(message)s"
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "app": {
            "formatter": "generic",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        }
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
        "app": {"handlers": ["app"], "level": "INFO", "propagate": False},
    },
}


# SLACK
# list of mention users for notification in slack
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL", default="")
ENVIRONMENT = os.getenv("ENVIRONMENT", default="DEVELOP")
SLACK_ALERT_CHANNEL_NAME = os.getenv("SLACK_ALERT_CHANNEL", default="hoethy")
SLACK_DEFAULT_MENTION_USERS = ["cloudythy"]
try:
    SLACK_MENTION_USERS: list[str] = json.loads(os.getenv("SLACK_MENTION_USERS"))
except Exception:
    SLACK_MENTION_USERS = SLACK_DEFAULT_MENTION_USERS

# EXPERIMENT
IS_EXPERIMENT: bool = True if os.getenv("IS_EXPERIMENT") else False
