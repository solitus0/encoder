import datetime
from dataclasses import dataclass
from typing import ClassVar, Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String, Text

from .database import Base


@dataclass
class Encode(Base):
    __tablename__ = "encodes"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    status = Column(String)
    source_path = Column(String)
    temp_path = Column(String)
    source_size = Column(Float, nullable=True)
    output_size = Column(Float, nullable=True)
    duration_in_seconds = Column(Integer, nullable=True)
    command = Column(JSON, nullable=True)
    media_uuid = Column(String, nullable=True)


@dataclass
class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    uuid = Column(String, nullable=False, index=True, unique=True)
    file_path = Column(String)
    file_name = Column(String)
    file_size = Column(Float, nullable=True)
    video_codec = Column(JSON, nullable=True)
    audio_codec = Column(JSON, nullable=True)
    subtitle_codec = Column(JSON, nullable=True)
    duration = Column(Float, nullable=True)
    dimensions = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    permissions: ClassVar[Optional[dict]] = {}


@dataclass
class Settings(Base):
    __tablename__ = "settings"

    id = Column(Integer, primary_key=True)
    key = Column(String, nullable=False, index=True, unique=True)
    value = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )
