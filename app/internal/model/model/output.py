from abc import ABC


class Output(ABC):
    ...


class MosquittoNormalOutput(Output):
    count: float

    def __init__(self, count) -> None:
        super().__init__()
        self.count = count
