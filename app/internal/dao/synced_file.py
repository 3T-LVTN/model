from sqlalchemy import Column, String

from app.internal.dao.base import BaseModel


class SyncedFile(BaseModel):
    __tablename__ = "synced_file"

    file_name = Column(None, String(255), unique=True)
