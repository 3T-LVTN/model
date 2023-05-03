from fastapi_camelcase import CamelModel


class UploadLocationRequest(CamelModel):
    file_path: str
