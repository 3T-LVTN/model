
import numpy as np
from typing import Callable, Tuple


def custom_metrics(y: float, y_pred: float) -> float:
    'function to get our custom metrics to pass into fit regularized'
    return np.abs(y - y_pred)


def get_custom_metrics() -> Callable[[float, float], float]:
    return custom_metrics
