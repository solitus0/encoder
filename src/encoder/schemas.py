from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

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
    duration_in_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class EncodeView(BaseEncode):
    media_uuid: str
    source_path: str
    source_size: float
    created_at: datetime
    output_size: Optional[float] = None
    command: Optional[str] = None
    duration_in_seconds: Optional[int] = None

    class Config:
        from_attributes = True


class EditEncodeStatus(BaseEncode):
    pass


class FinishEncode(BaseEncode):
    output_size: float
    duration_in_seconds: int


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


class EncodeCommand(BaseModel):
    preset: str
    media_ids: list[str]


class EncodeQuery(BaseModel):
    media_uuid: str


class ScanCommand(BaseModel):
    scan_path: str


class Preset(BaseModel):
    PresetName: str
    AudioBitrate: str
    AudioEncoder: str
    AudioMixdown: str
    AudioSamplerate: str
    FileFormat: str
    PictureWidth: Optional[int]
    PictureHeight: Optional[int]
    PresetName: str
    VideoEncoder: str
    VideoPreset: str
    VideoQualitySlider: int

    @validator("FileFormat")
    def check_file_format(cls, v):
        if v != "matroska":
            raise ValueError('Invalid FileFormat. Must be "matroska".')
        return v

    @validator("VideoPreset")
    def check_video_preset(cls, v):
        valid_presets = ["slow", "fast"]
        if v not in valid_presets:
            raise ValueError(
                f"Invalid VideoPreset value. Must be one of: {valid_presets}"
            )
        return v


class Disposition(BaseModel):
    default: Optional[int] = None
    dub: Optional[int] = None
    original: Optional[int] = None
    comment: Optional[int] = None
    lyrics: Optional[int] = None
    karaoke: Optional[int] = None
    forced: Optional[int] = None
    hearing_impaired: Optional[int] = None
    visual_impaired: Optional[int] = None
    clean_effects: Optional[int] = None
    attached_pic: Optional[int] = None
    timed_thumbnails: Optional[int] = None
    captions: Optional[int] = None
    descriptions: Optional[int] = None
    metadata: Optional[int] = None
    dependent: Optional[int] = None
    still_image: Optional[int] = None


class BaseStream(BaseModel):
    index: int
    codec_name: str
    codec_long_name: Optional[str] = None
    codec_tag_string: Optional[str] = None
    codec_tag: Optional[str] = None
    r_frame_rate: Optional[str] = None
    avg_frame_rate: Optional[str] = None
    time_base: Optional[str] = None
    start_pts: Optional[int] = None
    start_time: Optional[str] = None
    disposition: Optional[Disposition] = None
    tags: Optional[Dict[str, str]] = None


class VideoStream(BaseStream):
    codec_type: Optional[str] = Field("video", Literal=True)
    profile: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    coded_width: Optional[int] = None
    coded_height: Optional[int] = None
    closed_captions: Optional[int] = None
    film_grain: Optional[int] = None
    has_b_frames: Optional[int] = None
    sample_aspect_ratio: Optional[str] = None
    display_aspect_ratio: Optional[str] = None
    pix_fmt: Optional[str] = None
    level: Optional[int] = None
    color_range: Optional[str] = None
    color_space: Optional[str] = None
    color_transfer: Optional[str] = None
    color_primaries: Optional[str] = None
    chroma_location: Optional[str] = None
    field_order: Optional[str] = None
    refs: Optional[int] = None
    is_avc: Optional[str] = None
    nal_length_size: Optional[str] = None
    bits_per_raw_sample: Optional[str] = None
    extradata_size: Optional[int] = None


class AudioStream(BaseStream):
    codec_type: Optional[str] = Field("audio", Literal=True)
    profile: Optional[str] = None
    sample_fmt: Optional[str] = None
    sample_rate: Optional[str] = None
    channels: Optional[int] = None
    channel_layout: Optional[str] = None
    bits_per_sample: Optional[int] = None
    initial_padding: Optional[int] = None
    extradata_size: Optional[int] = None


class SubtitleStream(BaseStream):
    codec_type: Optional[str] = Field("subtitle", Literal=True)
    duration_ts: Optional[int] = None
    duration: Optional[str] = None
    extradata_size: Optional[int] = None


class AttachmentStream(BaseStream):
    codec_type: Optional[str] = Field("attachment", Literal=True)
    duration_ts: Optional[int] = None
    duration: Optional[str] = None
    extradata_size: Optional[int] = None


class Format(BaseModel):
    filename: Optional[str] = None
    nb_streams: Optional[int] = None
    nb_programs: Optional[int] = None
    format_name: Optional[str] = None
    format_long_name: Optional[str] = None
    start_time: Optional[str] = None
    duration: Optional[str] = None
    size: Optional[str]
    bit_rate: Optional[str] = None
    probe_score: Optional[int] = None
    tags: Optional[Dict[str, str]] = None


class MediaMetadata(BaseModel):
    streams: Optional[
        List[Union[VideoStream, AudioStream, SubtitleStream, AttachmentStream]]
    ] = None
    format: Optional[Format] = None

    def get_streams(self, type: str) -> List[BaseStream]:
        return [stream for stream in self.streams if stream.codec_type == type]

    def get_tag(self, tag: str) -> Optional[str]:
        return self.format.tags.get(tag)


class PaginationResponse(BaseModel):
    currentPage: int
    pageSize: int
    totalItems: int
    items: Optional[List[Media]] = None

    class Config:
        from_attributes = True


class SettingKeyEnum(str, Enum):
    temp_path = "temp_path"
    scan_path = "scan_path"


class SettingsBase(BaseModel):
    key: SettingKeyEnum
    value: str


class SettingsCreate(SettingsBase):
    pass


class SettingsUpdate(BaseModel):
    value: str


class SettingsInDB(SettingsBase):
    id: int
    created_at: datetime
    updated_at: datetime


class EncodeComplete(BaseModel):
    id: int
    duration: Optional[float] = None
