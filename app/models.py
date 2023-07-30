import datetime
from dataclasses import dataclass

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


@dataclass
class Encode(Base):
    __tablename__ = "encodes"

    id = Column(Integer, primary_key=True)
    output_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    duration_in_seconds = Column(Integer, nullable=True)
    source_file_size = Column(Float, nullable=True)
    output_file_size = Column(Float, nullable=True)
    cmd = Column(JSON, nullable=True)
    encode_hash = Column(String, nullable=True)

    media_id = Column(Integer, ForeignKey("media.id"), nullable=True)
    media = relationship("Media", back_populates="encodes")


@dataclass
class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    file_path = Column(String)
    file_size = Column(Float, nullable=True)
    video_codec = Column(JSON, nullable=True)
    audio_codec = Column(JSON, nullable=True)
    subtitle_codec = Column(JSON, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(
        DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow
    )

    encodes = relationship("Encode")
