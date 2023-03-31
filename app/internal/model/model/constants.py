
NORMAL_COLUMN = [
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
    "snow_depth",
    "visibility",
    "cloud_cover",
    "sea_level_pressure",
    "weather_type",
]

RANDOM_FACTOR_COLUMN = [
    "location_id"
]

PREDICTED_VAR = "predicted_var"

FORMULA = f"{PREDICTED_VAR} ~ {' + '.join(NORMAL_COLUMN)} + (1|{RANDOM_FACTOR_COLUMN})"

OUTPUT_MODEL_FOLDER = "app/internal/model/model_train_result/model_pkl"
