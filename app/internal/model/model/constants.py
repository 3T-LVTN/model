import os
NORMAL_COLUMNS = [
    'tempmax',
    'tempmin',
    'temp',
    'dew',
    'humidity',
    'precip',
    'precipprob',
    'precipcover'
]

RANDOM_FACTOR_COLUMN = "location_id"


PREDICTED_VAR = "value"

FORMULA = f"{PREDICTED_VAR} ~ {' + '.join(NORMAL_COLUMNS)}"

VC_FORMULA = {"location_id": "0 + C(location_id)"}
