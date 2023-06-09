
class ThirdServiceException(Exception):
    code = 503

    def __repr__(self) -> str:
        return f"third party service encounter problem"


class MissingFieldException(Exception):
    def __init__(self, *args: object, line: int = None, file_name: str = None) -> None:
        super().__init__(*args)
        self.line = line
        self.file_name = file_name

    def __repr__(self) -> str:
        return f"file_name {self.file_name if self.file_name is not None else ''} line {self.line if self.line is not None else ''} is missing data"


class GroupException(Exception):
    '''
    python 3.11 and onwards support group exception, but currently our app is using python 3.10
    we must implement our exception groups by our own.
    '''

    def __init__(self, exceptions: list[Exception]) -> None:
        self.exceptions = exceptions

    def __str__(self) -> str:
        return "\n".join({str(exception) for exception in self.exceptions})

    def __repr__(self) -> str:
        return "\n".join({str(exception) for exception in self.exceptions})
