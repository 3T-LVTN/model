from abc import ABC, abstractmethod
from typing import Optional, Protocol, ByteString
from app.adapter.file_service.s3_adapter import S3ClientAdapter


class IFileService(ABC):
    @abstractmethod
    def get_file_content(self, file_name: str) -> bytes: ...
    @abstractmethod
    def upload_file(self, content: bytes, file_name: Optional[str]): ...
    @abstractmethod
    def get_file_content_str(self, file_name: str) -> str: ...


class FileService(IFileService):
    def __init__(self):
        self.client = S3ClientAdapter()

    def get_file_content(self, file_name: str) -> bytes:
        return self.client.get_file_content(file_name)

    def upload_file(self, content: bytes, file_name: Optional[str]):
        self.client.upload_file(content, file_name)

    def get_file_content_str(self, file_name: str) -> str:
        return self.client.get_file_content(file_name).decode()


file_service = FileService()
