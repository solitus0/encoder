from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class EncodeBase(BaseModel):
    created_at: datetime
    duration_in_seconds: Optional[int] = None
    source_size: Optional[float] = None
    output_size: Optional[float] = None
    encode_hash: Optional[str] = None
    cmd: Optional[dict] = None


class Encode(EncodeBase):
    class Config:
        from_attributes = True


class BaseEncode(BaseModel):
    status: str = Field(
        default="started", description="Options: started, finished, failed"
    )


class EncodeProgress(BaseModel):
    media_uuid: str
    progress: float
    created_at: datetime
    file_name: str


class EncodeStatusEnum(str, Enum):
    queued = "queued"
    started = "started"
    finished = "finished"
    failed = "failed"


class InitializeEncode(BaseEncode):
    media_uuid: str
    source_path: str
    temp_path: str
    source_size: float
    command: list


class QueueEncode(BaseModel):
    id: int
    media_uuid: str
    source_path: str
    temp_path: str
    command: list
    created_at: datetime
    duration_in_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class EncodeView(BaseEncode):
    media_uuid: str
    source_path: str
    source_size: float
    created_at: datetime
    output_size: Optional[float] = None
    command: Optional[str] = None
    duration_in_seconds: Optional[float] = None

    class Config:
        from_attributes = True


class EditEncodeStatus(BaseEncode):
    pass


class FinishEncode(BaseEncode):
    output_size: float
    duration_in_seconds: float


class EncodeCommand(BaseModel):
    preset: str
    media_ids: list[str]


class EncodeQuery(BaseModel):
    media_uuid: str


class EncodeComplete(BaseModel):
    id: int
    duration: Optional[float] = None
