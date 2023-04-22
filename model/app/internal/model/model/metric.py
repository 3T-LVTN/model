
import numpy as np
from abc import ABC, abstractmethod
from typing import Callable, Tuple


class MetricsProvider(ABC):

    @abstractmethod
    def custom_metrics(self, y: float, y_pred: float) -> float: ...
    'function to get our custom metrics to pass into fit regularized'

    @abstractmethod
    def get_custom_metrics(self, *args, **kwargs) -> Callable[[float, float], float]: ...
    'function to get our custom metrics to pass into fit regularized'


class NormalMetricsProvider(MetricsProvider):
    def custom_metrics(self, y: float, y_pred: float) -> float:
        return np.abs(y - y_pred)

    def get_custom_metrics(self) -> Callable[[float, float], float]:
        return self.custom_metrics
