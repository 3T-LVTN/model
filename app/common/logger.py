import json
import logging
import textwrap
from typing import Optional, List

from app.common.util.json import JsonEncoder


class Colors:
    reset = '\033[0m'
    red = '\033[31m'
    green = '\033[32m'
    orange = '\033[33m'
    blue = '\033[34m'
    purple = '\033[35m'
    cyan = '\033[36m'
    yellow = '\033[93m'


# __loggers_config = {
#     'version': 1,
#     'formatters': {
#         'verbose': {
#             'format': '%(asctime)s | %(levelname)s | %(process)d | %(thread)d | %(filename)s:%('
#                       'lineno)d | request_id=%(request_id)s | %(message)s',
#             'datefmt': '%Y-%m-%d %H:%M:%S',
#         },
#         'dev': {
#             'format': f'{Colors.cyan}%(levelname)s::%(asctime)s{Colors.reset} | %(filename)s:%(lineno)d | '
#                       '%(message)s',
#             'datefmt': '%H:%M:%S',
#         },
#         'json': {
#             '()': 'app.core.log.formatters.CustomizedJSONFormatter',
#         }
#     },
#     'handlers': {
#         'console': {
#             'level': env_var.LOGGER_CONSOLE_LEVEL,
#             'class': 'logging.StreamHandler',
#             'formatter': env_var.LOGGER_CONSOLE_FORMATTER,
#             'filters': ['request_id'],
#         },
#     },
#     'filters': {
#         'request_id': {
#             '()': 'flask_log_request_id.RequestIDLogFilter',
#         },
#     },
#     'loggers': {
#         'main': {
#             'level': env_var.LOGGER_MAIN_LEVEL,
#             'handlers': env_var.LOGGER_MAIN_HANDLERS.split(','),
#             'propagate': True,
#         },
#     },
# }
#
# dictConfig(__loggers_config)


class CustomLoggerAdapter(logging.LoggerAdapter):
    """
    This example adapter expects the passed in dict-like object to have a
    'tags' key, whose value in brackets is prepended to the log message.
    """

    def process(self, msg, kwargs):
        tag_str = ''
        for tag in self.extra['tags']:
            tag_str += f'[{tag}]'
        if kwargs.get("extra") is None:
            kwargs["extra"] = {}
        elif isinstance(kwargs['extra'], dict):
            kwargs["extra"] = kwargs["extra"].copy()
        kwargs["extra"].update(self.extra)
        kwargs["extra"] = {
            "extraData": kwargs["extra"]
        }
        return f'{tag_str} {msg}', kwargs

    def escape_multiline_string(self, data) -> str:
        if isinstance(data, dict):
            data = json.dumps(data, cls=JsonEncoder)
        else:
            data = str(data)
        data = textwrap.dedent(data)
        lines = [line.strip().replace('\n', '').replace('\t', '') for line in data.splitlines()]
        return ''.join(lines)


def get(name=None, tags: Optional[List] = None) -> logging.LoggerAdapter:
    """
    Get logger
    :param name: name of logger
    :param tags: tags of logger
    :return: Logger

    """
    if name is None or name not in logging.root.manager.loggerDict:
        name = 'main'
    logging.captureWarnings(True)
    logger = logging.getLogger(name)
    logger = logging.LoggerAdapter(logger, {'tags': tags})
    return logger
