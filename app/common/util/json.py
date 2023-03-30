import datetime
import decimal
import logging
import enum
import json
from unittest import mock


_logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """Customized flask JSON Encoder"""

    def default(self, o):
        if hasattr(o, '__json__'):
            return o.__json__()
        if isinstance(o, decimal.Decimal):
            if o == o.to_integral_value():
                return int(o)
            else:
                return float(o)
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat(sep=' ')
        if isinstance(o, enum.Enum):
            return o.value
        if isinstance(o, tuple):
            return list(o)
        return super().default(o)


_default_json_encoder = JSONEncoder()
json_encode = _default_json_encoder.encode


def json_decode(s):
    """ Decode a json string
    :param str s: the JSON encoded string
    :rtype: mixed
    """
    return json.loads(s)
