from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, ValidationError, validator


class DimensionsMixin:
    @validator("dimensions")
    def validate_dimensions(cls, v):
        if not v:
            return v

        if v.count("x") != 1:
            raise ValidationError('Dimensions must have exactly one "x"')

        try:
            width, height = map(int, v.split("x"))
        except ValidationError:
            raise ValidationError('Dimensions must contain numbers separated by "x"')

        if width <= 0 or height <= 0:
            raise ValidationError("Width and height must be positive integers")

        return v


class QueueScan(BaseModel):
    source_path: str

    class Config:
        from_attributes = True


class MediaBase(BaseModel, DimensionsMixin):
    file_path: str
    file_name: str
    dimensions: Optional[str] = None
    file_size: Optional[float] = None
    video_codec: Optional[list] = None
    audio_codec: Optional[list] = None
    subtitle_codec: Optional[list] = None
    duration: Optional[float] = None


class MediaCreate(MediaBase):
    uuid: str


class Media(MediaBase):
    id: int
    uuid: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    permissions: Optional[dict] = None

    class Config:
        from_attributes = True


class OrderDirectionEnum(str, Enum):
    asc = "asc"
    desc = "desc"


class OrderByEnum(str, Enum):
    file_size = "file_size"
    file_path = "file_path"
    created_at = "created_at"
    updated_at = "updated_at"
    file_name = "file_name"


class FieldEnum(str, Enum):
    subtitle_codec = "subtitle_codec"
    audio_codec = "audio_codec"
    video_codec = "video_codec"
    file_name = "file_name"
    file_path = "file_path"
    dimensions = "dimensions"


class OperatorEnum(str, Enum):
    contains = "contains"


class PaginationFilter(BaseModel):
    page: int = 1
    pageSize: int = 50
    orderBy: OrderByEnum = Field(
        default="file_size",
        description=f"Options: {', '.join([item.value for item in OrderByEnum])}",
    )
    orderDirection: OrderDirectionEnum = Field(
        default="desc", description="Options: asc, desc"
    )
    field: Optional[FieldEnum] = None
    operator: Optional[OperatorEnum] = None
    value: Optional[str] = None


class ScanCommand(BaseModel):
    scan_path: str


class PaginationResponse(BaseModel):
    currentPage: int
    pageSize: int
    totalItems: int
    items: Optional[List[Media]] = None

    class Config:
        from_attributes = True
