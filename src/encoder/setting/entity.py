import datetime
from dataclasses import dataclass

from sqlalchemy import JSON, Column, DateTime, Integer, String

from ..database import Base


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
