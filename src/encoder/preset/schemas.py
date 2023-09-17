from typing import Optional
from pydantic import BaseModel, validator


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
