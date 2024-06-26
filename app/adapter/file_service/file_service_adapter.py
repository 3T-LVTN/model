from abc import ABC, abstractmethod
import logging
from typing import Optional, Protocol, ByteString
from botocore.exceptions import NoCredentialsError

from app.adapter.file_service.s3_adapter import S3ClientAdapter


class IFileService(ABC):
    @abstractmethod
    def get_file_content(self, file_name: str) -> bytes: ...
    @abstractmethod
    def upload_file(self, content: bytes, file_name: Optional[str]): ...
    @abstractmethod
    def get_file_content_str(self, file_name: str) -> str: ...
    @abstractmethod
    def get_list_file(self, prefix: str = None) -> list[str]: ...


class FileService(IFileService):
    def __init__(self):
        self.client = S3ClientAdapter()

    def get_connection(self):
        if self.client is not None:
            return
        try:
            self.client = S3ClientAdapter()
        except NoCredentialsError:
            logging.info("currently cannot connect file service")

    def get_file_content(self, file_name: str) -> bytes:
        self.get_connection()
        return self.client.get_file_content(file_name)

    def upload_file(self, content: bytes, file_name: Optional[str]):
        self.get_connection()
        self.client.upload_file(content, file_name)

    def get_file_content_str(self, file_name: str) -> str:
        self.get_connection()
        return self.client.get_file_content(file_name).decode()

    def get_list_file(self, prefix: str = None, postfixes: list[str] = None) -> list[str]:
        '''
        post fix is our implementation to filter extension by file
        because s3 do not support filter by postfix
        our more general ways to implement this is allow passing regexp but no one want to read regexp :(
        '''
        self.get_connection()
        return [file for file in self.client.get_list_file(prefix) if any([file.endswith(postfix) for postfix in postfixes])]


file_service = FileService()
