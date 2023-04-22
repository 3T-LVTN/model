from dataclasses import dataclass


@dataclass
class PredictionDTO:
    idx: int
    weight: float = None
