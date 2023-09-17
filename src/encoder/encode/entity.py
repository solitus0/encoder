import datetime
from dataclasses import dataclass
from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from encoder.database import Base


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
