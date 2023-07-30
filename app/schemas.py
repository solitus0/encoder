from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class EncodeBase(BaseModel):
    output_path: str
    created_at: datetime
    duration_in_seconds: Optional[int] = None
    source_file_size: Optional[float] = None
    output_file_size: Optional[float] = None
    cmd: Optional[dict] = None
    encode_hash: Optional[str] = None


class Encode(EncodeBase):
    class Config:
        orm_mode = True


class MediaBase(BaseModel):
    file_path: str
    file_size: Optional[float] = None
    video_codec: Optional[list] = None
    audio_codec: Optional[list] = None
    subtitle_codec: Optional[list] = None
    width: Optional[int] = None
    height: Optional[int] = None


class MediaCreate(MediaBase):
    pass


class Media(MediaBase):
    id: int
    encodes: List[Encode] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
