from enum import Enum


class Rate(str, Enum):
    SAFE = "SAFE"
    NORMAL = "NORMAL"
    LOW_RISK = "LOW RISK"
    HIGH_RISK = "HIGH RISK"


MAP_IDX_TO_RATE = {idx: value for idx, value in enumerate(Rate.__members__)}
