import os
NORMAL_COLUMNS = [
    "minimum_temperature",
    "maximum_temperature",
    "temperature",
    "dew_point",
    "relative_humidity",
    "heat_index",
    "wind_speed",
    "wind_gust",
    "wind_direction",
    "wind_chill",
    "precipitation",
    "precipitation_cover",
    "visibility",
    "cloud_cover",
    "sea_level_pressure",
]

RANDOM_FACTOR_COLUMN = "location_id"


PREDICTED_VAR = "value"

FORMULA = f"{PREDICTED_VAR} ~ {' + '.join(NORMAL_COLUMNS)}"

VC_FORMULA = {"location_id": "0 + C(location_id)"}

OUTPUT_MODEL_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "model_train_result"))
