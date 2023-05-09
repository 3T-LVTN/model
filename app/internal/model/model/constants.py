import os
NORMAL_COLUMNS = [
    "minimum_temperature",
    "maximum_temperature",
    "temperature",
    "dew_point",
    "relative_humidity",
    "precipitation",
    "precipitation_cover",
]

RANDOM_FACTOR_COLUMN = "location_id"


PREDICTED_VAR = "value"

FORMULA = f"{PREDICTED_VAR} ~ {' + '.join(NORMAL_COLUMNS)}"

VC_FORMULA = {"location_id": "0 + C(location_id)"}
