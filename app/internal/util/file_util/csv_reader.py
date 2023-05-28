from builtins import dict as _DictReadMapping
from csv import DictReader
from typing import Any, Sequence

from app.internal.model.model.constants import NORMAL_COLUMNS


class FieldNameMapper:
    '''
    user field name in csv might be mismatch with internal field name, this class will be file name handler
    for example user will input like str(b'nhi\xe1\xbb\x87t \xc4\x91\xe1\xbb\x99') (nhiệt độ in utf 8 encode),
    this class will map it to temperature in our csv reader
    '''
    __INTERNAL_FIELD_NAMES = NORMAL_COLUMNS+["value"]
    __USER_FIELD_NAMES: list[str] = []  # TODO: define later

    def __init__(self) -> None:
        self.internal_to_user_mapper = {internal: user for internal, user in zip(
            FieldNameMapper.__INTERNAL_FIELD_NAMES, FieldNameMapper.__USER_FIELD_NAMES)}

        self.user_to_internal_mapper = {user: internal for internal, user in zip(
            FieldNameMapper.__INTERNAL_FIELD_NAMES, FieldNameMapper.__INTERNAL_FIELD_NAMES)}
        self.user_to_internal_mapper.update({user: internal for internal, user in zip(
            FieldNameMapper.__INTERNAL_FIELD_NAMES, FieldNameMapper. __USER_FIELD_NAMES)})

    def to_user_fields(self, internal_fields: list[str]) -> list[str]:
        return [self.internal_to_user_mapper.get(field) for field in internal_fields]

    def to_internal_fields(self, user_fields: list[str]) -> list[str]:
        return [self.user_to_internal_mapper.get(field) for field in user_fields]

    def get_available_user_fields(self) -> Sequence[str]:
        return list(self.user_to_internal_mapper.keys())


__mapper = FieldNameMapper()


class CsvReader(DictReader):
    def __init__(self, f: str) -> None:
        self.mapper = __mapper
        super().__init__(f, fieldnames=self.mapper.get_available_user_fields())

    def __next__(self) -> dict[Any, str | Any]:
        content = super().__next__()
        return {self.mapper.to_internal_fields(key): val for key, val in content.items()}
