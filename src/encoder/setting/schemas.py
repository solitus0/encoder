from datetime import datetime
from enum import Enum
from pydantic import BaseModel, validator
import os


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


class SettingView(SettingsInDB):
    valid: bool
